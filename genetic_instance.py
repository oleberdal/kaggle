"""

"""
from random import random, shuffle
from copy import deepcopy


class HousePriceEstimator:
	def __init__(self, world, dna, dna_sequence, mutation_proneness=0.01, time_to_live=0, start_estimate=1):
		self.world = world
		self.generation = world.generation
		self.mutation_proneness = mutation_proneness
		self.dna = dna
		self.dna_sequence = dna_sequence
		self.initial_time_to_live = max(world.default_time_to_live, time_to_live)
		self.time_to_live = max(world.default_time_to_live, time_to_live)
		self.start_estimate = start_estimate
		self.score = -1

		self.mutate()
		self.estimate_prices()

	@staticmethod
	def create_operator_tree(target, first_agent=False):
		if len(target) == 1:
			return target[0]
		split_index = int((len(target) - 1) * random())
		# return {'+' if first_agent or random() <= 0.5 else '*': [HousePriceEstimator.create_operator_tree(target=target[:split_index + 1], first_agent=first_agent), HousePriceEstimator.create_operator_tree(target=target[split_index + 1:], first_agent=first_agent)]}
		return {'+' if first_agent or random() <= 1 else '*': [HousePriceEstimator.create_operator_tree(target=target[:split_index + 1], first_agent=first_agent), HousePriceEstimator.create_operator_tree(target=target[split_index + 1:], first_agent=first_agent)]}

	def estimate_prices(self, test=False):
		split_index = int(len(self.world.houses[2]) * self.world.training_split_percentage)

		if test:
			score = 0
			for house_number, house in enumerate(self.world.houses[2][split_index:]):
				score += abs(self.world.houses[3][split_index + house_number] - (self.start_estimate + self.calculate_house_estimate(house=house, dna_sequence=self.dna_sequence))) / self.world.houses[3][split_index + house_number]
			score /= len(self.world.houses[2][split_index:])
			return score
		self.score = 0
		for house_number, house in enumerate(self.world.houses[2][:split_index]):
			self.score += abs(self.world.houses[3][house_number] - (self.start_estimate + self.calculate_house_estimate(house=house, dna_sequence=self.dna_sequence))) / self.world.houses[3][house_number]
		self.score /= len(self.world.houses[2][:split_index])

	def calculate_house_estimate(self, house, dna_sequence):
		if isinstance(dna_sequence, dict):
			if '+' in dna_sequence:
				return self.calculate_house_estimate(house=house, dna_sequence=dna_sequence['+'][0]) + self.calculate_house_estimate(house=house, dna_sequence=dna_sequence['+'][1])
			else:
				return self.calculate_house_estimate(house=house, dna_sequence=dna_sequence['*'][0]) * self.calculate_house_estimate(house=house, dna_sequence=dna_sequence['*'][1])
		else:
			attribute_index = self.world.houses[0].index(dna_sequence) - 1
			if isinstance(house[attribute_index], str):
				if house[attribute_index] in self.dna[dna_sequence]:
					return self.dna[dna_sequence][house[attribute_index]]
				else:
					return 0
			else:
				# return self.dna[dna_sequence]['A(slope)'] * house[attribute_index] + self.dna[dna_sequence]['B(slope)']
				return self.dna[dna_sequence]['A(slope)'] * house[attribute_index]

	def reproduce_asexually(self, time_to_live=0):
		# return HousePriceEstimator(world=self.world, dna=deepcopy(self.dna), dna_sequence=self.dna_sequence, mutation_proneness=self.mutation_proneness, time_to_live=max(self.time_to_live, self.world.default_time_to_live, time_to_live), start_estimate=self.start_estimate)
		return HousePriceEstimator(world=self.world, dna=deepcopy(self.dna), dna_sequence=self.dna_sequence, mutation_proneness=self.mutation_proneness, start_estimate=self.start_estimate)

	# def reproduce_sexually(self):
	# 	return None

	def mutate(self):
		if random() <= self.mutation_proneness:
			self.start_estimate *= 1 + (0.1 - 0.2 * random() if random() <= self.mutation_proneness else 0)
			# self.start_estimate *= (2 - 2.1 * random() if random() <= self.mutation_proneness else 1)

		for attribute, encoding in self.dna.items():
			for category, value in encoding.items():
				self.dna[attribute][category] *= 1 + (0.1 - 0.2 * random() if random() <= self.mutation_proneness else 0)
				# self.dna[attribute][category] *= (2 - 2.1 * random() if random() <= self.mutation_proneness else 1)

		# if random() <= self.mutation_proneness:
		# 	full_tree_structure = sub_tree_structure = self.learn_tree_structure(dna_sequence=self.dna_sequence)
		# 	parent_split = int(full_tree_structure.count('¬') * random())
		# 	tree_path = ''
		# 	for parent_index in range(parent_split + 1):
		# 		first_part, trash, sub_tree_structure = sub_tree_structure.partition('¬')
		# 		for character in first_part[:-1]:
		# 			if character == '(':
		# 				tree_path += '0'
		# 			elif character == ',':
		# 				tree_path = tree_path[:-1]
		# 				tree_path += '1'
		# 			elif character == ')':
		# 				tree_path = tree_path[:-2]
		# 		tree_path += first_part[-1]
		#
		# 	sub_tree_structure, parentheses_count, string_index, leaf_nodes = sub_tree_structure[1:], 1, 0, []
		# 	while parentheses_count:
		# 		if sub_tree_structure[string_index] == ')':
		# 			parentheses_count -= 1
		# 		elif sub_tree_structure[string_index] == '(':
		# 			parentheses_count += 1
		# 		elif sub_tree_structure[string_index] == 'c':
		# 			leaf = sub_tree_structure[string_index + 2:sub_tree_structure.find(']', string_index)]
		# 			leaf_nodes.append(leaf)
		# 			string_index += len(leaf) + 2
		# 		string_index += 1
		#
		# 	shuffle(leaf_nodes)
		# 	self.reconstruct_tree(path=tree_path, dna_sequence=self.dna_sequence, leaf_attributes=leaf_nodes)

		# if random() < self.mutation_proneness:
		# 	self.mutation_proneness = min(1, self.mutation_proneness * (2 - 2 * random()))

	def learn_tree_structure(self, dna_sequence):
		if isinstance(dna_sequence, dict):
			key = list(dna_sequence.keys())[0]
			children = list(dna_sequence.values())
			return key + '¬(' + self.learn_tree_structure(children[0][0]) + ',' + self.learn_tree_structure(children[0][1]) + ')'
		else:
			return 'c[' + dna_sequence + ']'

	def reconstruct_tree(self, path, dna_sequence, leaf_attributes):
		if len(path) == 3:
			dna_sequence.get(path[0])[int(path[1])] = HousePriceEstimator.create_operator_tree(leaf_attributes)
		elif len(path) == 1:
			self.dna_sequence = HousePriceEstimator.create_operator_tree(leaf_attributes)
		else:
			self.reconstruct_tree(path=path[2:], dna_sequence=dna_sequence.get(path[0])[int(path[1])], leaf_attributes=leaf_attributes)

	def set(self, variable, content):
		if variable == 'dna':
			self.dna = content
		elif variable == 'dna_sequence':
			self.dna_sequence = content
		elif variable == 'score':
			self.score = content
		elif variable == 'generation':
			self.generation = content
			self.world.generation = int(max(self.world.generation, self.generation))
		elif variable == 'mutation_proneness':
			self.mutation_proneness = content
		elif variable == 'time_to_live':
			self.time_to_live = content
		elif variable == 'start_estimate':
			self.start_estimate = content
		else:
			print('Agent has no attribute denominated: "', variable, '".')