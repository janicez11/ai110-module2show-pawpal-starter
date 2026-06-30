# PawPal+ Project Reflection

## 1. System Design

Core Actions:
1. Add owner and pet info
2. Add tasks to a calendar system for feeding, walking, grooming, etc
3. Generate a daily plan based on availability and pet history



**a. Initial design**

- Briefly describe your initial UML design.
4 class objects: User, Pet, Task, and Scheduler
User can have multiple Pet objects.
Each pet contains tasks.


- What classes did you include, and what responsibilities did you assign to each?

1. User
    attributes:
    - name
    - pets []
    - availability
    - preferences
    methods:
    - add_pet()
    - set_availability()
    - set_preferences()
    - create_task()
    - delete_task()
    - get_task()

2. Pet
    attributes:
    - name
    - breed type
    - walk history
    - feeding history
    - groom history
    - medical history
    methods:
    - get_last walked()
    - get last fed
    - get last groomed
    - get last medical record
    - needs attention

3. Task
    attributes:
    - task title
    - task date/time 
    - duration
    - priority
    - recurrence
    - pet 
    methods:
    - assign to pet
    - is overdue
    - edit task

4. Scheduler
    attributes:
    - owner
    - tasks
    - generated plan
    methods:
    - generate_plan()
    - explain_plan()

**b. Design changes**

- Did your design change during implementation?
It did. Initially, I was unsure whether create task should be under the user or the pet. 
- If yes, describe at least one change and why you made it.
With AI help, it explained to me that it should stay within the user because it is the user's responsibility to create tasks and that the user would have all the info needed to create a task. 


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
