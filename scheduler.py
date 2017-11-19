"""
	Author : Victor Armegioiu
	Usage : python3 scheduler.py <MAX_PROCESSING_TIME> <problem>

"""

from copy import deepcopy
import time, sys

all_tasks = {}

START_TIME = 0
END_TIME = 1

starting_time = 0
MAX_PROCESSING_TIME = float(sys.argv[1])


class Task:
	def __init__(self, index, duration, deadline, predecessor_list, successor_list):
		self.index = index
		self.duration  = duration
		self.deadline = deadline
		self.predecessor_list = predecessor_list

	def __str__(self):
		return str(self.index) + ", " + str(self.duration) + ", " + str(self.deadline) + ", " + str(self.predecessor_list) 


class Processor:
	def __init__(self, proc_number):
		self.proc_number = proc_number
		self.processor_list = [[] for _ in range(proc_number)] # [(task_index, start_time)]
		self.scheduled_tasks = {} # {task_indek : (start_time, end_time, processor_index)}

	def last_task_on_processor(self, processor_index):
		return None if len(self.processor_list[processor_index]) == 0 else self.processor_list[processor_index][-1][0]

	def schedule_task(self, processor_index, task_index):
		start_time = 0

		if len(self.processor_list[processor_index]) == 0:
			self.processor_list[processor_index].append((task_index, start_time))

		else:
			last_task = self.last_task_on_processor(processor_index)
			start_time = self.scheduled_tasks[last_task][END_TIME]
			self.processor_list[processor_index].append((task_index, start_time))

		self.scheduled_tasks[task_index] = (start_time, start_time + all_tasks[task_index].duration, processor_index)

	def already_scheduled(self, task_index):
		return False if task_index not in self.scheduled_tasks else self.scheduled_tasks[task_index]

	def solution_cost(self):
		cost = 0
		for scheduled_task in self.scheduled_tasks.keys():
			cost += max(0, self.scheduled_tasks[scheduled_task][END_TIME] - all_tasks[scheduled_task].deadline)

		return cost

	def valid_final_state(self):
		for task in all_tasks:
			for dependency in all_tasks[task].predecessor_list:
				if dependency not in self.scheduled_tasks:
					return False
				else:
					if self.scheduled_tasks[dependency][END_TIME] > self.scheduled_tasks[task][START_TIME]:
						return False
		return True

	def valid_partial_state(self):
		for task in self.scheduled_tasks:
			for dependency in all_tasks[task].predecessor_list:
				if dependency not in self.scheduled_tasks:
					continue
				else:
					if self.scheduled_tasks[dependency][END_TIME] > self.scheduled_tasks[task][START_TIME]:
						return False
		return True

	def sort_processors(self):
		self.processor_list.sort(key=lambda processor : 0 if not processor else self.scheduled_tasks[processor[-1][0]][END_TIME])


class State:
	def __init__(self, processor_state, unscheduled_tasks):
		self.processor_state = processor_state
		self.unscheduled_tasks = unscheduled_tasks
		self.processor_count = processor_state.proc_number

	def is_final(self):
		return len(self.unscheduled_tasks) == 0

	def cost(self):
		return self.processor_state.solution_cost()

	def valid_final_scheduling(self):
		return self.processor_state.valid_final_state()

	def valid_partial_scheduling(self):
		return self.processor_state.valid_partial_state()

	def sort_processors(self):
		self.processor_state.sort_processors()

	def get_dag(self):
		g = [[] for _ in range(len(self.unscheduled_tasks))]
		in_degree = [0 for _ in range(len(self.unscheduled_tasks))]

		for task_index in self.unscheduled_tasks:
			for predecessor in self.all_tasks[task_index].predecessor_list:
				if predecessor not in self.unscheduled_tasks:
					continue

				g[predecessor - 1].append(task_index - 1)
				in_degree[task_index - 1] += 1

		return g, in_degree

	def kahn_score(self):
		g, in_degree = self.get_dag() 
		toposort_layer = [0 for _ in range(n)]
		q = []

		for u in range(len(g)):
			if in_degree[u] == 0:
				q.insert(0, u)

		while q:
			u = q.pop(0)

			for v in g[u]:
				in_degree[v] -= 1
				max_pred_level = 0

				for predecessor in all_tasks[v].predecessor_list:
					max_pred_level = max(max_pred_level, toposort_layer[predecessor - 1])

				toposort_layer[v] = 1 + max_pred_level

				if in_degree[v] == 0:
					q.insert(0, v)

		return toposort_layer

	def sort_unscheduled_tasks(self):
		self.unscheduled_tasks.sort(key=lambda task : (self.kahn_score()[task  - 1], all_tasks[task].deadline, all_tasks[task].duration))


def is_consistent(parent_task, current_state):
	satisfiable = 0
	for dependency in all_tasks[parent_task].predecessor_list:
		if dependency in current_state.unscheduled_tasks:
		
			for processor_index in range(current_state.processor_count):

				last_task = current_state.processor_state.last_task_on_processor(processor_index)
				dependency_start_time = 0 if not last_task else current_state.processor_state.scheduled_tasks[last_task][END_TIME]
				dependency_end_time = dependency_start_time + all_tasks[dependency].duration

				if current_state.processor_state.scheduled_tasks[parent_task][START_TIME] >= dependency_end_time:
					satisfiable += 1
					break
		else:
			satisfiable += 1

	return satisfiable == len(all_tasks[parent_task].predecessor_list)


min_cost = int(1e9)
best_solution = None

def solve(current_state, arc_consistency=False, kahn_layering=False, processor_sort=False):
	global min_cost
	global best_solution

	if time.clock() - starting_time > MAX_PROCESSING_TIME:
		for processor in best_solution.processor_list:
			if not processor:
				print(0)
			else:
				print(len(processor))
				for task in processor:
					print(task[0], ',', task[1], sep='')
		sys.exit()
	
	if current_state.is_final():
		if not current_state.valid_final_scheduling():
			return

		current_cost = current_state.cost()
		if current_cost < min_cost:
			min_cost = current_cost
			best_solution = deepcopy(current_state.processor_state)
		return

	else:

		if kahn_layering:
			current_state.sort_unscheduled_tasks()

		if processor_sort:
			current_state.sort_processors()

		for unscheduled_task in current_state.unscheduled_tasks:
			for processor_index in range(current_state.processor_count):
				if current_state.cost() < min_cost:

					dummy_state = deepcopy(current_state)
					dummy_state.unscheduled_tasks.remove(unscheduled_task)
					dummy_state.processor_state.schedule_task(processor_index, unscheduled_task)

					if arc_consistency and not is_consistent(unscheduled_task, dummy_state):
						continue

					if dummy_state.cost() >= min_cost or not dummy_state.valid_partial_scheduling():
						continue

					solve(dummy_state, arc_consistency, kahn_layering, processor_sort)


if __name__ == '__main__':
	first_line = list(map(int, input().split(',')))
	n, p = first_line[0], first_line[1]

	for i in range(n):
		line = list(map(int, input().split(',')))
		index, duration, deadline, predecessor_list = line[0], line[1], line[2], line[3:] 	
		all_tasks[index] = Task(index, duration, deadline, predecessor_list, [])

	processors = Processor(p)
	unscheduled_tasks = [i for i in range(1, n + 1)]

	initial_state = State(processors, unscheduled_tasks)
	start_time = time.clock()

	solve(initial_state)

	for processor in best_solution.processor_list:
		if not processor:
			print(0)
		else:
			print(len(processor))
			for task in processor:
				print(task[0], ',', task[1], sep='')