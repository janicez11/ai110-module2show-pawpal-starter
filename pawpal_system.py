from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Pet:
    name: str
    breed: str
    walk_history: list = field(default_factory=list)
    feeding_history: list = field(default_factory=list)
    grooming_history: list = field(default_factory=list)
    medical_history: list = field(default_factory=list)
    tasks: list = field(default_factory=list)

    def get_last_walked(self) -> datetime:
        """Return the most recent walk datetime, or None if never walked."""
        return max(self.walk_history) if self.walk_history else None

    def get_last_fed(self) -> datetime:
        """Return the most recent feeding datetime, or None if never fed."""
        return max(self.feeding_history) if self.feeding_history else None

    def get_last_groomed(self) -> datetime:
        """Return the most recent grooming datetime, or None if never groomed."""
        return max(self.grooming_history) if self.grooming_history else None

    def get_last_medical_record(self) -> dict:
        """Return the most recent medical record dict, or None if none exist."""
        return self.medical_history[-1] if self.medical_history else None

    def needs_attention(self) -> bool:
        """Return True if the pet is overdue for a walk (24h) or feeding (12h)."""
        now = datetime.now()
        last_walked = self.get_last_walked()
        last_fed = self.get_last_fed()
        if last_walked is None or (now - last_walked) > timedelta(hours=24):
            return True
        if last_fed is None or (now - last_fed) > timedelta(hours=12):
            return True
        return False


@dataclass
class Task:
    title: str
    duration: int          # in minutes
    priority: str
    recurrence: str = "daily"
    pet: Pet = None
    completed: bool = False
    last_completed: datetime = None
    scheduled_start: datetime = None
    scheduled_end: datetime = None

    def mark_complete(self) -> None:
        """Mark the task as done and record the current time as last_completed."""
        self.completed = True
        self.last_completed = datetime.now()

    def assign_to_pet(self, pet: Pet) -> None:
        """Link this task to a pet and add it to the pet's task list."""
        self.pet = pet
        if self not in pet.tasks:
            pet.tasks.append(self)

    def set_priority(self, priority: str) -> None:
        """Set the task priority, raising ValueError if not low/medium/high."""
        valid = {"low", "medium", "high"}
        if priority.lower() not in valid:
            raise ValueError(f"Priority must be one of {valid}")
        self.priority = priority.lower()

    def set_duration(self, duration: int) -> None:
        """Set the task duration in minutes, raising ValueError if not positive."""
        if duration <= 0:
            raise ValueError("Duration must be a positive number of minutes")
        self.duration = duration

    def is_overdue(self) -> bool:
        """Return True if the task has never been completed or exceeded its recurrence window."""
        if self.last_completed is None:
            return True
        thresholds = {
            "daily":   timedelta(days=1),
            "weekly":  timedelta(weeks=1),
            "monthly": timedelta(days=30),
        }
        threshold = thresholds.get(self.recurrence, timedelta(days=1))
        return (datetime.now() - self.last_completed) > threshold

    def to_dict(self) -> dict:
        """Serialize the task to a plain dictionary."""
        return {
            "title":          self.title,
            "duration":       self.duration,
            "priority":       self.priority,
            "recurrence":     self.recurrence,
            "pet":            self.pet.name if self.pet else None,
            "completed":      self.completed,
            "last_completed": self.last_completed.isoformat() if self.last_completed else None,
        }


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.availability: list = []
        self.preferences: dict = {}
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list if not already present."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's pet list if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def set_availability(self, windows: list) -> None:
        """Set the owner's available time windows as a list of start/end dicts."""
        self.availability = windows

    def add_task(self, task: Task) -> None:
        """Add an owner-level task if not already in the task list."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task_id) -> None:
        """Remove a task by object reference or integer index."""
        if isinstance(task_id, int):
            self.tasks.pop(task_id)
        elif task_id in self.tasks:
            self.tasks.remove(task_id)

    def get_tasks(self) -> list[Task]:
        """Return all tasks across the owner and every pet, with no duplicates."""
        all_tasks = list(self.tasks)
        for pet in self.pets:
            for task in pet.tasks:
                if task not in all_tasks:
                    all_tasks.append(task)
        return all_tasks

    def get_schedule(self) -> list:
        """Return all tasks sorted by priority (high first)."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(self.get_tasks(), key=lambda t: priority_order.get(t.priority, 99))


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: list[Task] = []
        self.generated_plan: list = []

    def generate_plan(self) -> list:
        """Fetch all tasks and sort them: overdue first, then by priority."""
        self.tasks = self.owner.get_tasks()
        priority_order = {"high": 0, "medium": 1, "low": 2}
        # Overdue tasks first, then sorted by priority
        self.generated_plan = sorted(
            self.tasks,
            key=lambda t: (not t.is_overdue(), priority_order.get(t.priority, 99))
        )
        return self.generated_plan

    def filter_by_time(self) -> list:
        """Assign sequential time slots to tasks that fit within the owner's availability windows."""
        tasks = self.generated_plan if self.generated_plan else self.tasks
        if not self.owner.availability:
            return tasks

        result = []
        task_queue = list(tasks)

        for window in self.owner.availability:
            if not (isinstance(window, dict) and "start" in window and "end" in window):
                continue
            cursor = window["start"]
            remaining = []
            for task in task_queue:
                slot_end = cursor + timedelta(minutes=task.duration)
                if slot_end <= window["end"]:
                    task.scheduled_start = cursor
                    task.scheduled_end = slot_end
                    result.append(task)
                    cursor = slot_end
                else:
                    remaining.append(task)
            task_queue = remaining

        return result

    def explain_plan(self) -> str:
        """Return a formatted string summarising every task in the current plan."""
        plan = self.generated_plan if self.generated_plan else self.generate_plan()
        if not plan:
            return f"{self.owner.name} has no tasks scheduled."

        lines = [f"Schedule for {self.owner.name}:"]
        for i, task in enumerate(plan, 1):
            pet_name = task.pet.name if task.pet else "general"
            status = "OVERDUE" if task.is_overdue() else "on track"
            lines.append(
                f"  {i}. [{task.priority.upper()}] {task.title} for {pet_name}"
                f" — {task.duration} min, {task.recurrence} ({status})"
            )
        return "\n".join(lines)
