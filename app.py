import streamlit as st
from pawpal_system import Pet, Task, Owner, Scheduler

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

st.subheader("Quick Demo Inputs (UI only)")
if "owners" not in st.session_state:
    st.session_state.owners = {}

# booleans used to toggle showing create new owner/pet/task input forms
if "show_add_owner" not in st.session_state:
    st.session_state.show_add_owner = False
if "show_add_pet" not in st.session_state:
    st.session_state.show_add_pet = False
if "show_add_task" not in st.session_state:
    st.session_state.show_add_task = False

# use st.session_state to store owner data during reruns
if st.session_state.owners:
    owner_name = st.selectbox("Owner", list(st.session_state.owners.keys()))
else:
    st.info("No owners yet. Add one below.")
    owner_name = None

if st.button("+ Add Owner"):
    st.session_state.show_add_owner = not st.session_state.show_add_owner

if st.session_state.show_add_owner:
    new_owner_name = st.text_input("Owner name", placeholder="Enter owner name")
    if st.button("Save owner") and new_owner_name:
        if new_owner_name not in st.session_state.owners:
            st.session_state.owners[new_owner_name] = Owner(name=new_owner_name)
        st.session_state.show_add_owner = False
        st.rerun()

# display pets when an owner is selected
if owner_name:
    owner = st.session_state.owners[owner_name]
    st.markdown(f"### {owner_name}'s Pets")

    # display owner's list of pets
    if owner.pets:
        st.table([{"name": p.name, "breed": p.breed} for p in owner.pets])
    else:
        st.info("No pets yet.")
    
    if st.button("+ Add Pet"):
        st.session_state.show_add_pet = not st.session_state.show_add_pet

    if st.session_state.show_add_pet:
        pet_name = st.text_input("Pet name", placeholder="Enter pet name")
        species = st.text_input("Species", placeholder="Enter pet breed")
        if st.button("Save pet") and pet_name:
            owner.add_pet(Pet(name=pet_name, breed=species))
            st.session_state.show_add_pet = False
            st.rerun()

# display tasks when an owner is selected
if owner_name:
    st.markdown(f"### {owner_name}'s Tasks")
    owner_only_tasks = [t for t in owner.tasks if t.pet is None]

    # owner level tasks
    with st.expander(f"General Tasks"):
        if owner_only_tasks:
            st.table([{"title": t.title, "duration (min)": t.duration, "priority": t.priority, "recurrence": t.recurrence, "done": "✔" if t.completed else ""} for t in owner_only_tasks])
        else:
            st.info(f"No tasks yet.")

    # pet level tasks, assigned to each pet
    for pet in owner.pets:
        with st.expander(f"{pet.name}'s Tasks"):
            if pet.tasks:
                st.table([{"title": t.title, "duration (min)": t.duration, "priority": t.priority, "recurrence": t.recurrence, "done": "✔" if t.completed else ""} for t in pet.tasks])
            else:
                st.info(f"No tasks for {pet.name} yet.")

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
        pet_options = ["No pet (owner task)"] + [p.name for p in owner.pets]
        assigned_pet = st.selectbox("Assign to pet", pet_options)
        if st.button("Save task"):
            task = Task(title=task_title, duration=int(duration), priority=priority, recurrence=recurrence)
            if assigned_pet != "No pet (owner task)":
                pet = next(p for p in owner.pets if p.name == assigned_pet)
                task.assign_to_pet(pet)
            owner.add_task(task)
            st.session_state.show_add_task = False
            st.rerun()

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

# calls Scheduler's generate_plan() and explain_plan() method
if st.button("Generate schedule"):
    if not owner_name:
        st.warning("Select an owner first.")
    else:
        scheduler = Scheduler(owner=st.session_state.owners[owner_name])
        plan = scheduler.generate_plan()
        if not plan:
            st.info("No tasks to schedule.")
        else:
            st.markdown("#### Schedule")
            st.code(scheduler.explain_plan())
            st.table([{
                "title": t.title,
                "pet": t.pet.name if t.pet else "—",
                "priority": t.priority,
                "duration (min)": t.duration,
                "recurrence": t.recurrence,
                "overdue": "yes" if t.is_overdue() else "no",
            } for t in plan])
