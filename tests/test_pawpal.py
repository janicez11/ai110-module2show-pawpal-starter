import pytest
from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, spawn_next_occurrence


@pytest.fixture
def task():
    return Task(title="Morning Walk", duration=30, priority="high", recurrence="daily")


def test_task_starts_incomplete(task):
    assert task.last_completed is None


def test_task_starts_with_no_completion_time(task):
    assert task.last_completed is None


def test_mark_complete_sets_completed_true(task):
    task.mark_complete()
    assert task.last_completed is not None


def test_mark_complete_sets_last_completed(task):
    task.mark_complete()
    assert task.last_completed is not None


def test_mark_complete_timestamps_now(task):
    before = datetime.now()
    task.mark_complete()
    after = datetime.now()
    assert before <= task.last_completed <= after


def test_mark_complete_clears_overdue(task):
    assert task.last_completed is None
    task.mark_complete()
    assert task.last_completed is not None


def test_task_overdue_again_after_recurrence_passes(task):
    task.last_completed = datetime.now() - timedelta(days=2)
    assert task.last_completed is not None
    task.mark_complete()
    assert task.last_completed is not None


def test_mark_complete_called_twice_updates_timestamp(task):
    task.mark_complete()
    first_time = task.last_completed
    task.mark_complete()
    assert task.last_completed >= first_time


# --- Pet task count tests ---

@pytest.fixture
def pet():
    return Pet(name="Buddy", type="Labrador")


def test_pet_starts_with_no_tasks(pet):
    assert len(pet.tasks) == 0


def test_assign_task_increases_count(pet):
    task = Task(title="Walk", duration=30, priority="high")
    task.assign_to_pet(pet)
    assert len(pet.tasks) == 1


def test_assign_multiple_tasks_increases_count(pet):
    Task(title="Walk",     duration=30, priority="high").assign_to_pet(pet)
    Task(title="Feeding",  duration=10, priority="high").assign_to_pet(pet)
    Task(title="Grooming", duration=45, priority="medium").assign_to_pet(pet)
    assert len(pet.tasks) == 3


def test_assign_same_task_twice_does_not_duplicate(pet):
    task = Task(title="Walk", duration=30, priority="high")
    task.assign_to_pet(pet)
    task.assign_to_pet(pet)
    assert len(pet.tasks) == 1


def test_assigned_task_is_in_pet_tasks(pet):
    task = Task(title="Walk", duration=30, priority="high")
    task.assign_to_pet(pet)
    assert task in pet.tasks


def test_assign_task_sets_task_pet_reference(pet):
    task = Task(title="Walk", duration=30, priority="high")
    task.assign_to_pet(pet)
    assert task.pet is pet


# --- Sorting / Scheduler tests ---

@pytest.fixture
def today():
    return datetime.now().replace(second=0, microsecond=0)


def make_task(title, priority, hour, minute, today, duration=20, recurrence="daily"):
    preferred = today.replace(hour=hour, minute=minute)
    return Task(
        title=title,
        duration=duration,
        priority=priority,
        recurrence=recurrence,
        preferred_start=preferred,
        scheduled_start=preferred,
    )


@pytest.fixture
def owner_with_window(today):
    o = Owner("Test Owner")
    o.set_availability([{
        "start": today.replace(hour=8, minute=0),
        "end":   today.replace(hour=12, minute=0),
    }])
    return o


def test_priority_sort_high_before_medium_before_low(today):
    """No availability set — plan must follow high → medium → low."""
    o = Owner("Test Owner")
    low    = make_task("Low Task",    "low",    9,  0, today)
    medium = make_task("Medium Task", "medium", 9, 30, today)
    high   = make_task("High Task",   "high",  10,  0, today)
    for t in [low, medium, high]:
        o.add_task(t)
    plan = Scheduler(o).generate_plan()
    assert plan[0] is high
    assert plan[1] is medium
    assert plan[2] is low


def test_chronological_order_with_availability(today, owner_with_window):
    """With availability set, tasks must be returned in ascending scheduled_start order."""
    t1 = make_task("First",  "low",  11,  0, today)
    t2 = make_task("Second", "low",   9,  0, today)
    t3 = make_task("Third",  "low",   8, 30, today)
    for t in [t1, t2, t3]:
        owner_with_window.add_task(t)
    plan = Scheduler(owner_with_window).generate_plan()
    starts = [t.scheduled_start for t in plan]
    assert starts == sorted(starts)


def test_out_of_order_input_returns_chronological(today, owner_with_window):
    """Tasks added in reverse time order still come out in chronological order."""
    late  = make_task("Late",  "high", 11, 0, today)
    early = make_task("Early", "high",  8, 0, today)
    owner_with_window.add_task(late)
    owner_with_window.add_task(early)
    plan = Scheduler(owner_with_window).generate_plan()
    assert plan[0] is early
    assert plan[1] is late


def test_same_preferred_time_priority_is_tiebreaker(today, owner_with_window):
    """Two tasks at the same preferred time — higher priority must be scheduled first."""
    low  = make_task("Low",  "low",  9, 0, today)
    high = make_task("High", "high", 9, 0, today)
    owner_with_window.add_task(low)
    owner_with_window.add_task(high)
    plan = Scheduler(owner_with_window).generate_plan()
    assert plan[0] is high


def test_task_outside_window_is_unscheduled(today, owner_with_window):
    """A task preferred outside the availability window must not appear in the plan."""
    inside  = make_task("Inside",  "high",  9, 0, today)
    outside = make_task("Outside", "high", 14, 0, today)  # after 12pm window
    owner_with_window.add_task(inside)
    owner_with_window.add_task(outside)
    scheduler = Scheduler(owner_with_window)
    plan = scheduler.generate_plan()
    assert outside not in plan
    assert outside in scheduler.unscheduled


# --- Recurrence tests ---

@pytest.fixture
def daily_task(today):
    return Task(
        title="Morning Walk",
        duration=30,
        priority="high",
        recurrence="daily",
        preferred_start=today.replace(hour=8, minute=0),
        scheduled_start=today.replace(hour=8, minute=0),
    )


def test_daily_task_creates_next_occurrence(daily_task, today):
    """Completing a daily task spawns a new task scheduled for the following day."""
    owner = Owner("Test Owner")
    owner.add_task(daily_task)
    daily_task.mark_complete()
    next_task = spawn_next_occurrence(daily_task, owner)
    assert next_task is not None
    assert next_task.preferred_start.date() == (today + timedelta(days=1)).date()


def test_daily_next_occurrence_in_owner_tasks(daily_task):
    """The spawned next occurrence must be registered in owner.tasks."""
    owner = Owner("Test Owner")
    owner.add_task(daily_task)
    daily_task.mark_complete()
    next_task = spawn_next_occurrence(daily_task, owner)
    assert next_task in owner.tasks


def test_next_occurrence_preserves_attributes(daily_task):
    """The spawned task must carry over title, duration, priority, and recurrence."""
    owner = Owner("Test Owner")
    daily_task.mark_complete()
    next_task = spawn_next_occurrence(daily_task, owner)
    assert next_task.title      == daily_task.title
    assert next_task.duration   == daily_task.duration
    assert next_task.priority   == daily_task.priority
    assert next_task.recurrence == daily_task.recurrence


def test_none_recurrence_does_not_spawn(today):
    """A one-time task must not produce a follow-up task."""
    owner = Owner("Test Owner")
    task = Task(
        title="One-time Task",
        duration=20,
        priority="low",
        recurrence="none",
        preferred_start=today.replace(hour=9, minute=0),
        scheduled_start=today.replace(hour=9, minute=0),
    )
    owner.add_task(task)
    task.mark_complete()
    result = spawn_next_occurrence(task, owner)
    assert result is None
    assert len(owner.tasks) == 1  # only the original


def test_no_scheduled_start_does_not_spawn(today):
    """A recurring task with no scheduled_start must not produce a follow-up task."""
    owner = Owner("Test Owner")
    task = Task(
        title="Unscheduled Walk",
        duration=20,
        priority="high",
        recurrence="daily",
        preferred_start=today.replace(hour=9, minute=0),
        scheduled_start=None,
    )
    owner.add_task(task)
    task.mark_complete()
    result = spawn_next_occurrence(task, owner)
    assert result is None


def test_daily_task_with_pet_assigns_pet_to_next_occurrence(daily_task):
    """The spawned next occurrence for a pet task must be linked to the same pet."""
    owner = Owner("Test Owner")
    pet = Pet(name="Buddy", type="Labrador")
    owner.add_pet(pet)
    daily_task.assign_to_pet(pet)
    owner.add_task(daily_task)
    daily_task.mark_complete()
    next_task = spawn_next_occurrence(daily_task, owner)
    assert next_task.pet is pet
    assert next_task in pet.tasks


# --- Conflict detection tests ---

def test_same_preferred_time_second_task_flagged(today, owner_with_window):
    """Two tasks at the same preferred time — the bumped task must appear in conflicts."""
    t1 = make_task("Walk",    "high",   9, 0, today, duration=30)
    t2 = make_task("Feeding", "medium", 9, 0, today, duration=20)
    owner_with_window.add_task(t1)
    owner_with_window.add_task(t2)
    scheduler = Scheduler(owner_with_window)
    scheduler.generate_plan()
    assert len(scheduler.conflicts) == 1
    assert "Feeding" in scheduler.conflicts[0]


def test_non_overlapping_tasks_no_conflict(today, owner_with_window):
    """Tasks that fit end-to-end at their preferred times must not generate any conflicts."""
    t1 = make_task("Walk",    "high", 8,  0, today, duration=30)  # 8:00–8:30
    t2 = make_task("Feeding", "high", 8, 30, today, duration=20)  # 8:30–8:50
    owner_with_window.add_task(t1)
    owner_with_window.add_task(t2)
    scheduler = Scheduler(owner_with_window)
    scheduler.generate_plan()
    assert scheduler.conflicts == []


def test_long_task_pushes_following_task_into_conflict(today, owner_with_window):
    """A task that runs past the next task's preferred time must flag the displaced task."""
    t1 = make_task("Long Walk", "high",   9,  0, today, duration=60)  # 9:00–10:00
    t2 = make_task("Feeding",   "medium", 9, 30, today, duration=20)  # preferred 9:30, bumped to 10:00
    owner_with_window.add_task(t1)
    owner_with_window.add_task(t2)
    scheduler = Scheduler(owner_with_window)
    scheduler.generate_plan()
    assert len(scheduler.conflicts) == 1
    assert "Feeding" in scheduler.conflicts[0]


def test_multiple_overlapping_tasks_all_flagged(today, owner_with_window):
    """Three tasks at the same preferred time — the second and third must both be flagged."""
    t1 = make_task("Task A", "high",   9, 0, today, duration=20)
    t2 = make_task("Task B", "medium", 9, 0, today, duration=20)
    t3 = make_task("Task C", "low",    9, 0, today, duration=20)
    for t in [t1, t2, t3]:
        owner_with_window.add_task(t)
    scheduler = Scheduler(owner_with_window)
    scheduler.generate_plan()
    assert len(scheduler.conflicts) == 2


def test_conflict_message_names_displaced_task(today, owner_with_window):
    """The conflict message must include the title of the bumped task."""
    t1 = make_task("Morning Walk", "high",   9, 0, today, duration=30)
    t2 = make_task("Grooming",     "medium", 9, 0, today, duration=20)
    owner_with_window.add_task(t1)
    owner_with_window.add_task(t2)
    scheduler = Scheduler(owner_with_window)
    scheduler.generate_plan()
    assert any("Grooming" in msg for msg in scheduler.conflicts)


def test_single_task_at_preferred_time_no_conflict(today, owner_with_window):
    """A single task that fits in the window at its preferred time generates no conflict."""
    t = make_task("Walk", "high", 9, 0, today, duration=30)
    owner_with_window.add_task(t)
    scheduler = Scheduler(owner_with_window)
    scheduler.generate_plan()
    assert scheduler.conflicts == []
