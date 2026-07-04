import pytest
from datetime import datetime, timedelta
from pawpal_system import Task, Pet


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
