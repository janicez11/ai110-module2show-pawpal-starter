from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Pet:
    name: str
    breed: str
    walk_history: list = field(default_factory=list)
    feeding_history: list = field(default_factory=list)
    grooming_history: list = field(default_factory=list)
    medical_history: list = field(default_factory=list)

    def get_last_walked(self) -> datetime:
        pass

    def get_last_fed(self) -> datetime:
        pass

    def get_last_groomed(self) -> datetime:
        pass

    def get_last_medical_record(self) -> dict:
        pass

    def needs_attention(self) -> bool:
        pass


@dataclass
class Task:
    title: str
    duration: int
    priority: str
    recurrence: str = "daily"
    pet: Pet = None

    def assign_to_pet(self, pet: Pet) -> None:
        pass

    def set_priority(self, priority: str) -> None:
        pass

    def set_duration(self, duration: int) -> None:
        pass

    def is_overdue(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.availability: list = []
        self.preferences: dict = {}
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def set_availability(self, windows: list) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass

    def get_schedule(self) -> list:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: list[Task] = []
        self.generated_plan: list = []

    def generate_plan(self) -> list:
        pass

    def filter_by_time(self) -> list:
        pass

    def explain_plan(self) -> str:
        pass
