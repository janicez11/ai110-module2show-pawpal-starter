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

1. **Launch the app** — run `streamlit run app.py` and open the local URL in your browser. You'll see the PawPal+ title and a description of the app.
2. **Add an owner** — click `+ Add Owner`, type a name, and click `Save owner`. The owner's name will appear in the dropdown at the top.
3. **Add a pet** — with the owner selected, click `+ Add Pet`, enter a name and species, then click `Save pet`. The pet appears in a table under the owner's name.
4. **Add tasks** — Open an expander under Tasks, owner or pet. Click `+ Add Task` to open the task form. Fill in the title, duration (minutes), priority (low/medium/high), recurrence, date, time.  Click `Save task` to add it.
5. **View tasks** — tasks appear under expandable sections labeled "General Tasks" (owner-level) or by pet name. Each row shows the title, date, time, duration, priority, and recurrence.
6. **Complete a task** — check the checkbox next to a task to mark it done. It disappears from the list. If the task is recurring, a new instance for the next occurrence is automatically created.
7. **Set availability** — scroll to the Availability section and click `+ Add Availability Window`. Enter a start and end time, then click `Save window`. This defines when the owner is free to do tasks.
8. **Generate a schedule** — click `Generate schedule`. The app fits all of today's pending tasks into the availability window, sorted by preferred time and priority.
9. **Review the results** — a green success banner confirms the schedule is ready. Any tasks that were bumped or couldn't fit appear as yellow conflict warnings. The schedule table shows each task's start time, end time, pet, priority, duration, and recurrence.
10. **Read the explanation** — below the table, a plain-text explanation describes why each task was placed at its time and notes any tasks that could not be scheduled.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
