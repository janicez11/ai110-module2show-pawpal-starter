from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create Owner ---
owner = Owner("Jamie")

# --- Create Pets ---
buddy = Pet(name="Buddy", breed="Labrador")
luna  = Pet(name="Luna",  breed="Persian Cat")

owner.add_pet(buddy)
owner.add_pet(luna)

# --- Create Tasks with different durations ---
morning_walk = Task(title="Morning Walk",   duration=30,  priority="high",   recurrence="daily")
feeding      = Task(title="Feeding",        duration=10,  priority="high",   recurrence="daily")
grooming     = Task(title="Grooming",       duration=45,  priority="medium", recurrence="weekly")

morning_walk.assign_to_pet(buddy)
feeding.assign_to_pet(luna)
grooming.assign_to_pet(buddy)

# Mark feeding as recently completed so it shows "on track"
feeding.last_completed = datetime.now() - timedelta(hours=6)

# --- Set owner availability (9am-11am today) ---
today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
owner.set_availability([{"start": today, "end": today.replace(hour=11)}])

# --- Run Scheduler ---
scheduler = Scheduler(owner)
scheduler.generate_plan()

fitting  = scheduler.filter_by_time()
date_str = datetime.now().strftime("%a %b %d")
width    = 42

windows = owner.availability
window_str = (
    f"{windows[0]['start'].strftime('%I:%M %p')} - {windows[0]['end'].strftime('%I:%M %p')}"
    if windows else "No window set"
)

print("=" * width)
print(f"{'TODAY\'S SCHEDULE':^{width}}")
print(f"{f'{owner.name}  |  {date_str}':^{width}}")
print("=" * width)

# Group tasks by pet, preserving scheduler order
pets_seen = []
for task in fitting:
    if task.pet not in pets_seen:
        pets_seen.append(task.pet)

for pet in pets_seen:
    header = f"  {pet.name.upper()} ({pet.breed})"
    print()
    print(header)
    print("  " + "-" * (len(header) - 2))
    for task in fitting:
        if task.pet is pet:
            flag     = "[!]" if task.is_overdue() else "[ ]"
            status   = "OVERDUE" if task.is_overdue() else "on track"
            time_str = (
                f"{task.scheduled_start.strftime('%I:%M %p')} - {task.scheduled_end.strftime('%I:%M %p')}"
                if task.scheduled_start else f"{task.duration} min"
            )
            print(f"  {flag} {task.title:<18} {time_str:<25} {status}")

print()
print("=" * width)
print(f"  {len(fitting)} task(s) fit your {window_str} window")
print("=" * width)
