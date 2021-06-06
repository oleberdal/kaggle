"""
Author: Ole Kjølseth Berdal
Created: 09.01.2020
Version: Python 3.7.4

INSERT DESCRIPTION HERE
"""
import os

from time import time, sleep
from random import random, shuffle
from json import loads

import file_reader
import genetic_instance

TRAINING_DATA = 'train.csv'
TEST_DATA = 'test.csv'

PROMPT_TIME = 60


class World:
	def __init__(self, name, houses, population_limit, default_time_to_live=3, population=[], generation=0, training_split_percentage=.7):
		self.name = name
		self.houses = houses
		self.population_limit = population_limit
		self.default_time_to_live = default_time_to_live
		self.population = population
		self.generation = generation
		self.training_split_percentage = training_split_percentage

	def reproduce(self):
		new_agents = []
		# new_agents = [self.create_random_agent()]

		# total_score = sum(agent.score for agent in self.population[:self.population_limitation])
		# for agent in self.population[:self.population_limitation]:
		# 	score_so_far, random_threshold = 0, random()
		# 	for partner in self.population[:self.population_limitation]:
		# 		score_so_far += partner.score
		# 		if random_threshold < (total_score - score_so_far) / total_score:
		# 			new_agents.append(agent.reproduce_sexually())
		# 			new_agents.append(agent.reproduce_sexually())
		# 			break

		for agent in self.population[:self.population_limit]:
			# if agent.score * random() < self.population[0].score:
			# 	new_agents.append(agent.reproduce_asexually())
			new_agents.append(agent.reproduce_asexually())
			new_agents.append(agent.reproduce_asexually())
			new_agents.append(agent.reproduce_asexually())

		# for agent in self.population[self.population_limitation:]:
		# 	if agent.time_to_live > self.default_time_to_live:
		# 		new_agents.append(agent.reproduce_asexually())

		self.population += new_agents

	def calculate_fitness(self):
		self.population.sort(key=lambda x: x.score, reverse=False)

	def population_control(self):
		# survivors = []
		#
		# for agent in self.population[:self.population_limitation]:
		# 	if agent.time_to_live > 0:
		# 		survivors.append(agent)
		# 	agent.time_to_live -= 1
		#
		# for agent in self.population[self.population_limitation:2 * self.population_limitation]:
		# 	if random() < (agent.time_to_live - 1) / (agent.initial_time_to_live + 1) or agent.time_to_live > self.default_time_to_live:
		# 		survivors.append(agent)
		# 	agent.time_to_live -= 1
		#
		# for agent in self.population[2 * self.population_limitation:]:
		# 	if random() < ((agent.time_to_live - 2) / (agent.initial_time_to_live + 2))**2 or agent.time_to_live > 10 - self.default_time_to_live:
		# 		survivors.append(agent)
		# 	agent.time_to_live -= 1
		#
		# self.population[0].time_to_live += 1 if random() >= 1 / len(self.population) else -1
		# self.population = survivors
		self.population = self.population[:self.population_limit]

	def create_random_agent(self):
		dna = dict()
		for key, variations in self.houses[4].items():
			# dna[key] = {variation: 0.1 * random() for variation in variations}
			dna[key] = {variation: random() for variation in variations}

		dna_sequence = self.houses[0][1:-1]
		shuffle(dna_sequence)
		return genetic_instance.HousePriceEstimator(world=self, dna=dna, dna_sequence=genetic_instance.HousePriceEstimator.create_operator_tree(target=dna_sequence), mutation_proneness=0.01, time_to_live=10)


def main():
	train_data = file_reader.read_data(file_name=TRAINING_DATA, train=True)
	test_data = file_reader.read_data(file_name=TEST_DATA)

	environment = World(name='test_universeXY', houses=train_data, population_limit=1, default_time_to_live=1, training_split_percentage=1)

	if not os.path.exists(environment.name):
		environment.population = [environment.create_random_agent()]
	else:
		with open(os.path.join(environment.name, 'agents')) as agents_file:
			all_lines = agents_file.readlines()
		for agent in all_lines:
			variables = {}

			variable_split = agent.split('=')
			for variable_index in range(agent.count('=')):
				key = variable_split[variable_index][variable_split[variable_index].rfind(' ') + 1:]
				value = variable_split[variable_index + 1][:variable_split[variable_index + 1].rfind(' ') - 1]
				variables[key] = float(value) if is_numerical(value) else loads(value.replace('\'', '"'))

			add_agent_to_world(world=environment, agent=variables)

	print('generation ', environment.generation, ': trained MAPE=', environment.population[0].score, ', test MAPE=', environment.population[0].estimate_prices(test=True), sep='', end='\n')
	# print('generation ', environment.generation, ': trained MAPE=', environment.population[0].score, sep='', end='\n')

	mode_prompt, last_save = input('Train or test? '), time()
	while mode_prompt.lower() == 'train':
		environment.generation += 1

		environment.reproduce()
		environment.calculate_fitness()
		environment.population_control()

		# print('generation ', environment.generation, ' (', len(environment.population), '): ', environment.population[0].score, '-', environment.population[min(environment.population_limitation, len(environment.population) - 1)].score, ' (mutation proneness: ', environment.population[0].mutation_proneness, ')', sep='')

		if time() - last_save > PROMPT_TIME:
			if not os.path.exists(environment.name):
				os.mkdir(environment.name)
			with open(os.path.join(environment.name, 'agents'), 'w') as universe_file:
				for agent in environment.population[:environment.population_limit]:
					universe_file.write('score=' + str(agent.score) + ', generation=' + str(agent.generation) + ', dna_sequence=' + str(agent.dna_sequence) + ', dna=' + str(agent.dna) + ', start_estimate=' + str(agent.start_estimate) + '\n')

			print('generation ', environment.generation, ': trained MAPE=', environment.population[0].score, ', test MAPE=', environment.population[0].estimate_prices(test=True), sep='', end='\n')
			# print('generation ', environment.generation, ': trained MAPE=', environment.population[0].score, sep='', end='\n')

			print('Saved progress.\n')
			# mode_prompt = input('Train or test? ')
			last_save = time()

	if mode_prompt.lower() == 'test':
		environment.training_split_percentage = 0
		environment.houses = test_data
		top_agent = environment.population[0]

		with open(os.path.join(file_reader.DATA_FOLDER, 'test_predictions.csv'), 'w') as results_file:
			results_file.write('Id,SalePrice\n')
			for house_number, house in enumerate(environment.houses[2]):
				results_file.write(str(int(environment.houses[1][house_number])) + ',' + str(top_agent.calculate_house_estimate(house, top_agent.dna_sequence)) + '\n')


def is_numerical(string):
	numerical = False
	is_negative = string[0] == '-'
	string = string[1 if is_negative else 0:]
	broken_up = string.replace(',', '.').split('.')
	if len(broken_up) <= 2:
		numerical = True
		for part in broken_up:
			if not part.isdecimal():
				numerical = False
				break
	return numerical


def add_agent_to_world(world, agent):
	agent_shell = world.create_random_agent()
	for key, value in agent.items():
		agent_shell.set(variable=key, content=value)

	world.population.append(agent_shell)


if __name__ == '__main__':
	start_time = time()
	main()
	print('\nExecution time: %s seconds.' % (time() - start_time))
