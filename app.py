import streamlit as st
from datetime import datetime, time
from pawpal_system import Pet, Task, Owner, Scheduler, spawn_next_occurrence

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("PawPal+")

# hold owner data between reruns
if "owners" not in st.session_state:
    st.session_state.owners = {}

# booleans used to toggle input form displays
if "show_add_owner" not in st.session_state:
    st.session_state.show_add_owner = False
if "show_add_pet" not in st.session_state:
    st.session_state.show_add_pet = False
if "show_add_task" not in st.session_state:
    st.session_state.show_add_task = False
if "show_add_window" not in st.session_state:
    st.session_state.show_add_window = False

# owners saved in the session will be displayed here
if st.session_state.owners:
    owner_name = st.selectbox("Owner", list(st.session_state.owners.keys()))
else:
    st.info("Add an owner to start.")
    owner_name = None

# add new owner form
if st.button("+ Add Owner"):
    st.session_state.show_add_owner = not st.session_state.show_add_owner

if st.session_state.show_add_owner:
    new_owner_name = st.text_input("Owner name", placeholder="Enter owner name")
    if st.button("Save owner") and new_owner_name:
        if new_owner_name not in st.session_state.owners:
            st.session_state.owners[new_owner_name] = Owner(name=new_owner_name)
        st.session_state.show_add_owner = False
        st.rerun()


# display pets when an owner is selected or created
if owner_name:
    owner = st.session_state.owners[owner_name]
    st.markdown(f"### {owner_name}'s Pets")

    # display owner's list of pets
    if owner.pets:
        st.table([{"name": p.name, "type": p.type} for p in owner.pets])
    else:
        st.info("No pets yet.")
    
    # add new pet form
    if st.button("+ Add Pet"):
        st.session_state.show_add_pet = not st.session_state.show_add_pet

    if st.session_state.show_add_pet:
        pet_name = st.text_input("Pet name", placeholder="Enter pet name")
        species = st.text_input("Species", placeholder="Enter pet type")
        if st.button("Save pet") and pet_name:
            owner.add_pet(Pet(name=pet_name, type=species))
            st.session_state.show_add_pet = False
            st.rerun()

def render_task_list(tasks, key_prefix, empty_msg, owner):
    """Render an interactive task list with a checkbox per row.

    Filters out completed tasks, shows a header row and one row per active task.
    Checking a task marks it complete and, for recurring tasks, creates the next
    occurrence before triggering a rerun.

    Args:
        tasks:      List of Task objects to display.
        key_prefix: Unique string prefix for checkbox widget keys.
        empty_msg:  Message shown when there are no active tasks.
        owner:      Owner instance used to register recurring follow-up tasks.
    """
    active = [t for t in tasks if t.last_completed is None]
    if not active:
        st.info(empty_msg)
        return
    cols = st.columns([0.5, 3, 1.5, 1.5, 1, 1.5, 1.5])
    for col, label in zip(cols, ["✔", "Title", "Date", "Time", "Min", "Priority", "Recurrence"]):
        col.markdown(f"**{label}**")
    for t in active:
        cols = st.columns([0.5, 3, 1.5, 1.5, 1, 1.5, 1.5], vertical_alignment="center")
        with cols[0]:
            # when task is completed, check recurring attribute and create new task if needed
            if st.checkbox("", key=f"{key_prefix}_{id(t)}", label_visibility="collapsed"):
                t.mark_complete()
                spawn_next_occurrence(t, owner)
                st.rerun()
        # displays all attributes for each Task
        cols[1].write(t.title)
        cols[2].write(t.preferred_start.strftime("%b %d") if t.preferred_start else "—")
        cols[3].write(t.preferred_start.strftime("%I:%M %p") if t.preferred_start else "—")
        cols[4].write(str(t.duration))
        cols[5].write(t.priority)
        cols[6].write(t.recurrence)

# display tasks when an owner is selected
if owner_name:
    st.markdown(f"### {owner_name}'s Tasks")
    owner_only_tasks = [t for t in owner.tasks if t.pet is None]

    # owner level tasks
    with st.expander("General Tasks"):
        render_task_list(owner_only_tasks, f"owner_{owner_name}", "No tasks yet.", owner)

    # pet level tasks, assigned to each pet
    for pet in owner.pets:
        with st.expander(f"{pet.name}'s Tasks"):
            render_task_list(pet.tasks, f"pet_{pet.name}", f"No tasks for {pet.name} yet.", owner)

    # add new task
    if st.button("+ Add Task"):
        st.session_state.show_add_task = not st.session_state.show_add_task

    if st.session_state.show_add_task:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_title = st.text_input("Task title", placeholder="Enter task title")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col4:
            recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly", "monthly"])
        col5, col6 = st.columns(2)
        with col5:
            preferred_date = st.date_input("Date", value=datetime.now().date())
        with col6:
            preferred_time = st.time_input("Time", value=time(8, 0))
        pet_options = ["No pet (owner task)"] + [p.name for p in owner.pets]
        assigned_pet = st.selectbox("Assign to pet", pet_options)
        if st.button("Save task"):
            task = Task(title=task_title, duration=int(duration), priority=priority, recurrence=recurrence)
            task.preferred_start = datetime.combine(preferred_date, preferred_time)
            task.scheduled_start = task.preferred_start
            if assigned_pet != "No pet (owner task)":
                pet = next(p for p in owner.pets if p.name == assigned_pet)
                task.assign_to_pet(pet)
            owner.add_task(task)
            st.session_state.show_add_task = False
            st.rerun()

st.divider()

# set owner availability
if owner_name:
    st.markdown(f"### {owner_name}'s Availability")
    owner = st.session_state.owners[owner_name]

    if owner.availability:
        st.table([{
            "start": w["start"].strftime("%I:%M %p"),
            "end":   w["end"].strftime("%I:%M %p"),
        } for w in owner.availability])
    else:
        st.info("No availability windows set. Set up availability to build schedule.")

    # add new availability window
    if st.button("+ Add Availability Window"):
        st.session_state.show_add_window = not st.session_state.show_add_window

    if st.session_state.show_add_window:
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start time", value=time(9, 0))
        with col2:
            end_time = st.time_input("End time", value=time(17, 0))
        if st.button("Save window"):
            today = datetime.now().date()
            new_window = {
                "start": datetime.combine(today, start_time),
                "end":   datetime.combine(today, end_time),
            }
            if new_window["start"] < new_window["end"]:
                owner.availability.append(new_window)
                st.session_state.show_add_window = False
                st.rerun()
            else:
                st.error("End time must be after start time.")

if owner_name:
    st.subheader("Build Schedule")

    owner_has_availability = st.session_state.owners[owner_name].availability
    if not owner_has_availability:
        st.info("Add at least one availability window above to generate a schedule.")

    # generate today's plan
    if owner_has_availability and st.button("Generate schedule"):
        owner = st.session_state.owners[owner_name]
        owner.set_availability(owner.availability)
        scheduler = Scheduler(owner=owner)
        plan = scheduler.generate_plan()
        if not plan:
            st.info("No tasks to schedule.")
        else:
            if scheduler.conflicts:
                for msg in scheduler.conflicts:
                    st.warning(msg)
            st.markdown(f"#### Today's Schedule — {datetime.now().strftime('%A, %B %d %Y')}")
            st.code(scheduler.explain_plan())
            st.table([{
                "start": t.scheduled_start.strftime("%I:%M %p") if t.scheduled_start else "—",
                "end": t.scheduled_end.strftime("%I:%M %p") if t.scheduled_end else "—",
                "title": t.title,
                "pet": t.pet.name if t.pet else "—",
                "priority": t.priority,
                "duration (min)": t.duration,
                "recurrence": t.recurrence,
            } for t in plan])
