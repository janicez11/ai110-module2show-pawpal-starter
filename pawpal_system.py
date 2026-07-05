from dataclasses import dataclass, field
from datetime import datetime, timedelta


RECURRENCE_DELTA = {
    "daily":   timedelta(days=1),
    "weekly":  timedelta(weeks=1),
    "monthly": timedelta(days=30),
}


@dataclass
class Pet:
    name: str
    type: str
    tasks: list = field(default_factory=list)


@dataclass
class Task:
    title: str
    duration: int          # in minutes
    priority: str
    recurrence: str = "daily"
    pet: Pet = None
    last_completed: datetime = None
    preferred_start: datetime = None
    scheduled_start: datetime = None
    scheduled_end: datetime = None

    def mark_complete(self) -> None:
        """Mark the task as done and record the current time as last_completed."""
        self.last_completed = datetime.now()

    def assign_to_pet(self, pet: Pet) -> None:
        """Link this task to a pet and add it to the pet's task list."""
        self.pet = pet
        if self not in pet.tasks:
            pet.tasks.append(self)



def spawn_next_occurrence(task: "Task", owner: "Owner") -> "Task | None":
    """Create the next occurrence of a recurring task and register it with the owner.

    Returns the new Task, or None if the task has no recurrence delta or no scheduled_start.
    """
    delta = RECURRENCE_DELTA.get(task.recurrence)
    if not delta or not task.scheduled_start:
        return None
    next_task = Task(
        title=task.title,
        duration=task.duration,
        priority=task.priority,
        recurrence=task.recurrence,
        preferred_start=task.preferred_start + delta,
        scheduled_start=task.scheduled_start + delta,
    )
    if task.pet:
        next_task.assign_to_pet(task.pet)
    owner.add_task(next_task)
    return next_task


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.availability: list = []
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list if not already present."""
        if pet not in self.pets:
            self.pets.append(pet)

    def set_availability(self, windows: list) -> None:
        """Set the owner's available time windows as a list of start/end dicts."""
        self.availability = windows

    def add_task(self, task: Task) -> None:
        """Add an owner-level task if not already in the task list."""
        if task not in self.tasks:
            self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks across the owner and every pet, with no duplicates."""
        all_tasks = list(self.tasks)
        for pet in self.pets:
            for task in pet.tasks:
                if task not in all_tasks:
                    all_tasks.append(task)
        return all_tasks

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> list:
        """Return tasks optionally filtered by completion status and/or pet name."""
        tasks = self.get_tasks()
        if completed is not None:
            tasks = [t for t in tasks if (t.last_completed is not None) == completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet and t.pet.name == pet_name]
        return tasks


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: list[Task] = []
        self.generated_plan: list = []
        self.conflicts: list = []
        self.unscheduled: list = []

    def generate_plan(self) -> list:
        """Fetch all incompleted tasks for today and build a plan. With availability set, delegates sorting to filter_by_time()."""
        today = datetime.now().date()
        self.tasks = [
            t for t in self.owner.get_tasks()
            if t.last_completed is None and t.preferred_start and t.preferred_start.date() == today
        ]
        if self.owner.availability:
            self.generated_plan = self.filter_by_time()
        else:
            priority_order = {"high": 0, "medium": 1, "low": 2}
            self.generated_plan = sorted(
                self.tasks,
                key=lambda t: priority_order.get(t.priority, 99)
            )
        return self.generated_plan

    def check_conflict(self, task: Task, preferred: datetime, start: datetime) -> None:
        """Append a warning to self.conflicts if a task could not be placed at its preferred time."""
        pet_label = f"for {task.pet.name}" if task.pet else f"for {self.owner.name}"
        if start > preferred:
            self.conflicts.append(
                f"Task '{task.title}' ({pet_label}) preferred {preferred.strftime('%I:%M %p')} but bumped to {start.strftime('%I:%M %p')} due to a conflict with a prior task."
            )

    def filter_by_time(self) -> list:
        """Sort tasks by preferred start time, then fit them into availability windows."""
        tasks = self.generated_plan if self.generated_plan else self.tasks
        if not self.owner.availability:
            return tasks

        self.conflicts = []
        self.unscheduled = []
        priority_order = {"high": 0, "medium": 1, "low": 2}
        task_queue = sorted(
            tasks,
            key=lambda t: (t.preferred_start.strftime("%H:%M"), priority_order.get(t.priority, 99))
        )

        result = []

        for window in self.owner.availability:
            if not (isinstance(window, dict) and "start" in window and "end" in window):
                continue
            cursor = window["start"]
            remaining = []
            for task in task_queue:
                preferred = window["start"].replace(
                    hour=task.preferred_start.hour,
                    minute=task.preferred_start.minute,
                    second=0,
                    microsecond=0,
                )
                if preferred < window["start"] or preferred >= window["end"]:
                    remaining.append(task)
                    continue
                start = max(preferred, cursor)
                slot_end = start + timedelta(minutes=task.duration)
                if slot_end <= window["end"]:
                    self.check_conflict(task, preferred, start)
                    task.scheduled_start = start
                    task.scheduled_end = slot_end
                    result.append(task)
                    cursor = slot_end
                else:
                    remaining.append(task)
            task_queue = remaining

        self.unscheduled = task_queue
        for task in self.unscheduled:
            pet_label = f"for {task.pet.name}" if task.pet else f"for {self.owner.name}"
            self.conflicts.append(
                f"Task '{task.title}' ({pet_label}) preferred {task.preferred_start.strftime('%I:%M %p')} could not fit in any availability window and was not scheduled."
            )

        return result

    def explain_plan(self) -> str:
        """Return a plain-text explanation of why each task was scheduled when it was."""
        plan = self.generated_plan if self.generated_plan else self.generate_plan()
        if not plan:
            return f"{self.owner.name} has no tasks scheduled for today."

        recurrence_reasons = {
            "daily":   "It recurs daily, so it needs to be done today.",
            "weekly":  "It recurs weekly and is due this week.",
            "monthly": "It recurs monthly and is due this month.",
            "none":    "It is a one-time task.",
        }

        conflict_titles = {msg.split("'")[1] for msg in self.conflicts}

        lines = [f"{self.owner.name}'s schedule explanation for today:\n"]
        for i, task in enumerate(plan, 1):
            pet_name = task.pet.name if task.pet else self.owner.name
            time_str = (
                f"{task.scheduled_start.strftime('%I:%M %p')} to {task.scheduled_end.strftime('%I:%M %p')}"
                if task.scheduled_start and task.scheduled_end
                else "an unassigned slot"
            )
            recurrence_note = recurrence_reasons.get(task.recurrence, "")
            conflict_note = (
                "It's start time was adjusted to avoid overlapping with another task. Sorted by priority."
                if task.title in conflict_titles else
                "It was placed at its preferred time."
            )

            lines.append(
                f"{i}. {task.title} (for {pet_name}) — scheduled {time_str}, {task.duration} min.\n"
                f"   {recurrence_note} {conflict_note}"
            )
        if self.unscheduled:
            lines.append("\nCould not be scheduled:")
            for task in self.unscheduled:
                pet_name = task.pet.name if task.pet else self.owner.name
                lines.append(
                    f"  - {task.title} (for {pet_name}) — preferred {task.preferred_start.strftime('%I:%M %p')}"
                    f" but could not fit in any availability window."
                )

        return "\n".join(lines)
