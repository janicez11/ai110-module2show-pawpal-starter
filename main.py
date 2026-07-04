from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create Owner ---
owner = Owner("Jamie")

# --- Create Pets ---
buddy = Pet(name="Buddy", type="Labrador")
luna  = Pet(name="Luna",  type="Persian Cat")

owner.add_pet(buddy)
owner.add_pet(luna)

# --- Create Tasks with times intentionally out of order, varying durations ---
today = datetime.now().replace(second=0, microsecond=0)

vet_visit    = Task(title="Vet Visit",      duration=60,  priority="high",   recurrence="monthly", preferred_start=today.replace(hour=14, minute=0), scheduled_start=today.replace(hour=14, minute=0))
evening_walk = Task(title="Evening Walk",   duration=30,  priority="high",   recurrence="daily",   preferred_start=today.replace(hour=17, minute=30), scheduled_start=today.replace(hour=17, minute=30))
grooming     = Task(title="Grooming",       duration=45,  priority="medium", recurrence="weekly",  preferred_start=today.replace(hour=10, minute=0),  scheduled_start=today.replace(hour=10, minute=0))
feeding      = Task(title="Feeding",        duration=10,  priority="high",   recurrence="daily",   preferred_start=today.replace(hour=7,  minute=30), scheduled_start=today.replace(hour=7,  minute=30))
morning_walk = Task(title="Morning Walk",   duration=25,  priority="high",   recurrence="daily",   preferred_start=today.replace(hour=8,  minute=0),  scheduled_start=today.replace(hour=8,  minute=0))
playtime     = Task(title="Playtime",       duration=20,  priority="low",    recurrence="daily",   preferred_start=today.replace(hour=9,  minute=0),  scheduled_start=today.replace(hour=9,  minute=0))

# Conflict task 1: same time as morning_walk (8:00 AM) — should be bumped
brush_teeth  = Task(title="Brush Teeth",    duration=15,  priority="medium", recurrence="daily",   preferred_start=today.replace(hour=8,  minute=0),  scheduled_start=today.replace(hour=8,  minute=0))
# Conflict task 2: before the window (7:30 AM, same as feeding) — should warn about early time
medication   = Task(title="Medication",     duration=10,  priority="high",   recurrence="daily",   preferred_start=today.replace(hour=7,  minute=30), scheduled_start=today.replace(hour=7,  minute=30))

morning_walk.assign_to_pet(buddy)
evening_walk.assign_to_pet(buddy)
grooming.assign_to_pet(buddy)
feeding.assign_to_pet(luna)
vet_visit.assign_to_pet(luna)
playtime.assign_to_pet(buddy)
brush_teeth.assign_to_pet(luna)

# Mark feeding as recently completed
feeding.last_completed = datetime.now() - timedelta(hours=6)

owner.add_task(vet_visit)
owner.add_task(evening_walk)
owner.add_task(grooming)
owner.add_task(feeding)
owner.add_task(morning_walk)
owner.add_task(playtime)
owner.add_task(brush_teeth)
owner.add_task(medication)

# --- Set availability window (8am-12pm) ---
window_start = today.replace(hour=8,  minute=0)
window_end   = today.replace(hour=12, minute=0)
owner.set_availability([{"start": window_start, "end": window_end}])

width      = 52
date_str   = today.strftime("%a %b %d")
window_str = f"{window_start.strftime('%I:%M %p')} - {window_end.strftime('%I:%M %p')}"

# --- Run Scheduler ---
scheduler = Scheduler(owner)
plan      = scheduler.generate_plan()
scheduled = plan

print("=" * width)
print(f"{'PAWPAL+ SCHEDULE':^{width}}")
print(f"{f'{owner.name}  |  {date_str}':^{width}}")
print("=" * width)

# --- Conflict warnings ---
if scheduler.conflicts:
    print(f"\n  CONFLICT WARNINGS")
    print("  " + "-" * (width - 2))
    for msg in scheduler.conflicts:
        print(f"  [!] {msg}")

# --- Scheduled tasks (sorted by preferred time, fit within window) ---
print(f"\n  SCHEDULED  ({window_str})")
print("  " + "-" * (width - 2))
for task in scheduled:
    time_str  = f"{task.scheduled_start.strftime('%I:%M')} - {task.scheduled_end.strftime('%I:%M %p')}"
    pet_label = task.pet.name if task.pet else "general"
    print(f"  {task.title:<20} {time_str:<22} {pet_label}")

# --- Tasks that didn't fit the window ---
unscheduled = [t for t in plan if t not in scheduled]
if unscheduled:
    print(f"\n  OUTSIDE WINDOW (not scheduled)")
    print("  " + "-" * (width - 2))
    for task in unscheduled:
        preferred = task.scheduled_start.strftime("%I:%M %p") if task.scheduled_start else "no time set"
        print(f"  [-] {task.title:<18} preferred: {preferred}")

# --- filter_tasks() demos ---
print(f"\n  FILTER: incomplete tasks for Buddy")
print("  " + "-" * (width - 2))
for task in owner.filter_tasks(completed=False, pet_name="Buddy"):
    print(f"  - {task.title} ({task.priority}, {task.duration} min)")

print(f"\n  FILTER: completed tasks (all pets)")
print("  " + "-" * (width - 2))
done = owner.filter_tasks(completed=True)
if done:
    for task in done:
        print(f"  - {task.title} (last done: {task.last_completed.strftime('%I:%M %p')})")
else:
    print("  No completed tasks.")

print()
print("=" * width)
print(f"  {len(scheduled)} of {len(plan)} task(s) fit the {window_str} window")
print("=" * width)
