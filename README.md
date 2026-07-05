# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:


====================================================
                  PAWPAL+ SCHEDULE                  
                Jamie  |  Sat Jul 04                
====================================================

  CONFLICT WARNINGS
  --------------------------------------------------
  [!] Task 'Brush Teeth' (for Luna) preferred 08:00 AM but bumped to 08:25 AM due to a conflict with a prior task.
  [!] Task 'Medication' (for the owner) preferred 07:30 AM could not fit in any availability window and was not scheduled.
  [!] Task 'Vet Visit' (for Luna) preferred 02:00 PM could not fit in any availability window and was not scheduled.
  [!] Task 'Evening Walk' (for Buddy) preferred 05:30 PM could not fit in any availability window and was not scheduled.

  SCHEDULED  (08:00 AM - 12:00 PM)
  --------------------------------------------------
  Morning Walk         08:00 - 08:25 AM       Buddy
  Brush Teeth          08:25 - 08:40 AM       Luna
  Playtime             09:00 - 09:20 AM       Buddy
  Grooming             10:00 - 10:45 AM       Buddy

  FILTER: incomplete tasks for Buddy
  --------------------------------------------------
  - Evening Walk (high, 30 min)
  - Grooming (medium, 45 min)
  - Morning Walk (high, 25 min)
  - Playtime (low, 20 min)

  FILTER: completed tasks (all pets)
  --------------------------------------------------
  - Feeding (last done: 02:08 PM)

====================================================
  4 of 4 task(s) fit the 08:00 AM - 12:00 PM window
====================================================

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

- Task Completion: mark_complete sets last_completed to a non-None datetime.
- Pet/task assignment: assign_to_pet links the task bidirectionally, adds it to pet.tasks, does not duplicate on repeated calls, and correctly tracks multiple distinct tasks.
- Sorting / scheduling: tasks are returned in chronological order by scheduled_start regardless of insertion order. Same preferred time uses priority as a tiebreaker. Tasks outside the window land in unscheduled, not the plan.
- Recurrence Spawning: Completing a daily task creates a follow-up task dated the next day
- Duplicate preferred times bump the lower-priority task and record exactly one conflict naming that task.

# Run with coverage:
pytest --cov
```

Sample test output:

```
========================================================= test session starts =========================================================
platform win32 -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\janic\OneDrive\Desktop\Projects\AI_Codepath_Course\ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 31 items                                                                                                                     

tests\test_pawpal.py ...............................                                                                             [100%]

========================================================= 31 passed in 0.12s ==========================================================
```

Confidence Level: 5 stars

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.filter_by_time(), generate_plan() | gets list of tasks that are incompleted and due today, then sorts it by time. |
| Task Filtering | filter_tasks() | filters tasks by completion or pet names |
| Conflict handling | Scheduler.check_conflicts() | check for tasks with same start time and uses priority as tie breaker to place them one after another.|
| Recurring tasks | render_task_list() | upon task completion, check if it is a recurring task. If it is, then create a new instance of it immediately.|

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
