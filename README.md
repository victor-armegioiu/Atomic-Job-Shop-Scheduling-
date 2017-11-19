# Atomic Job Shop Scheduling
Non-preemptive job shop scheduling with atomic jobs.

This program attempts to find solutions to a problem that can be formalized as such : 
- Given N Tasks and P identical independent machines, find a scheduling that minimizes the makespan
- A task is characterized as a tuple of the following values (index, duration, deadline, precedence_list[indices of other tasks that have to be completed before this task can be scheduled])
- We assume that each processor has the same computational power, therefore any processor completes task t_i in t_i.duration time units

Several input files are included within this repository, each of them describes a problem as such :
- First line of the file consists of two numbers (N, P) = (number of tasks, number of available machines)
- Next, N lines where each line is comprised of several numbers such that : 1st number is the index of the task, 2nd number is the duration of the task, 3rd is the deadline, and at most N - 1 numbers that comprise a list of indices of tasks that have to be completed before the current task.

My scheduler may be used as such : python3 scheduler.py <MAX_PROCESSING_TIME_SECONDS> <input_problem>

Given the NP hardness of the problem, I used several heuristic approaches that include :
- backtracking with pruning (invalid states are pruned)
- sorting the list of the processors on the current at each iteration by the finish time of the last task on each processor
- arc-consistency
- sorting the list of the unscheduled tasks by their level in the current topological order of the set of unscheduled tasks:
  * here we use a modified version of Kahn's algorithm to incrementally find the level of a vertex, where level(vertex) = max(predecessor_level) + 1
  * by topologically layering the tasks we can converge on correct solutions faster
  * we use the deadlines and duration as tie breakers for tasks that share the same level

