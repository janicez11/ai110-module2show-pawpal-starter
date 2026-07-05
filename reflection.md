# PawPal+ Project Reflection

## 1. System Design

Core Actions:
1. Add owner and pet info
2. Add tasks to a calendar system for feeding, walking, grooming, etc
3. Generate a daily plan based on availability and pet history



**a. Initial design**

- Briefly describe your initial UML design.
4 class objects: User, Pet, Task, and Scheduler
Each user will contain Pet information and Task information where they can create tasks for each pet. 
The Scheduler will have access to Owner information to access tasks and pets for scheduling tasks.


- What classes did you include, and what responsibilities did you assign to each?

1. User
    attributes:
    - name
    - pets []
    - availability
    methods:
    - add_pet()
    - set_availability()
    - create_task()
    - get_task()

2. Pet
    attributes:
    - name
    - breed type

3. Task
    attributes:
    - task title
    - task date/time 
    - duration
    - priority
    - recurrence
    - pet 
    methods:
    - mark_complete()
    - assign to pet

4. Scheduler
    attributes:
    - owner
    - tasks
    - conflicts
    - unscheduled
    - generated plan
    methods:
    - generate_plan()
    - check_conflict()
    - filter_by_time()
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
It used priority, overdue, availability window.
- How did you decide which constraints mattered most?
I kept availability window because that is the most important constraint. If the owner is
not even avaialble then the task cannot be scheduled. Then I used priority as a tie breaker for conflicting tasks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
Being strict with preferred start time. Originally, the scheduler placed tasks before the availability window start time to maximize how many tasks got scheduled for the day, but that ignored the owner's timing intent. Instead, I switched it to just not schedule those tasks and display with a warning message. 

- Why is that tradeoff reasonable for this scenario?
This provides the most accuracy of scheduling and time for the owner. Tasks with a perferred time specified should not be pushed back to make time for another task that was specified outside the available window. A better option would be to schedule those remaining tasks in time slots that fit throughout the day once the preferred ones get scheduled.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used Claude to refine my design brainstorming in the beginning. It helped me figure out the relationships each class should have once I had most of the attributes and methods down. It also helped me with debugging and implementing the logic I had to code. Finally, it created pytests based on the test points I gave it.

- What kinds of prompts or questions were most helpful?
Finding out where a certain piece of code is used in multiple areas, so that when I need to change one instance of it, I can ask AI to help me find all of them and update them all so that I can prevent bugs later on. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
There were many instances where AI gave me wrong advise or overlooked some code logic. The code where it handles the unscheduled tasks due to being outside availability window, AI created redundant code to store them. More loops were used to store them into another list when it could be directly stored. 

- How did you evaluate or verify what the AI suggested?
While it wouldn't have thrown any errors, I was able to catch that by reading through each line of code and understanding what is happening. I asked the AI why it did that and suggested my solution, and the AI apologized for it lol. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Task Completion: mark_complete sets last_completed to a non-None datetime.
- Pet/task assignment: assign_to_pet links the task bidirectionally, adds it to pet.tasks, does not duplicate on repeated calls, and correctly tracks multiple distinct tasks.
- Sorting / scheduling: tasks are returned in chronological order by scheduled_start regardless of insertion order. Same preferred time uses priority as a tiebreaker. Tasks outside the window land in unscheduled, not the plan.
- Recurrence Spawning: Completing a daily task creates a follow-up task dated the next day
- Duplicate preferred times bump the lower-priority task and record exactly one conflict naming that task.

- Why were these tests important?
These were the core logic to this app. Without testing these, I can't be too confident that the basic functions and the scheduler works.

**b. Confidence**

- How confident are you that your scheduler works correctly? 5 stars
- What edge cases would you test next if you had more time? 
Tasks that misses window 1 but fits window 2.
Tasks that are too long to fit into any window.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
How I designed the UI to help with the flow of the logic behind the app.
When a user lands on the app, they are constrained to first enter owner information to continue. Only when owner is saved, then pets can be added. Once pets are saved, then you can check each pet's tasks and add accordingly.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would implement the function to add in the unscheduled tasks back into the schedule based on avaialble blocks and ignoring the preferred time in the second round.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI is so powerful. As long as I have the logic and vision in my head, I can ask it to create starter code that I can build easier off of. My biggest struggle is starting from scratch, so having AI to help with that speeds things up. 
