"""
Author: Ole Kjølseth Berdal
Created: 09.01.2020
Version: Python 3.7.4

This module reads a file and turns it into the appropriate data structure.
"""
import os

DATA_FOLDER = 'data'


def read_data(file_name, train=False):
	file_path = os.path.join(DATA_FOLDER, file_name)

	file_name_extension = file_name.rsplit('.')[1].lower()
	file_name_extension_separators = {'csv': ','}

	output = [[], [], [], [], []]

	with open(file_path, 'r') as file:
		all_lines = file.readlines()

	if file_name_extension in file_name_extension_separators:
		file_name_extension_separator = file_name_extension_separators[file_name_extension]

		for line in all_lines:
			if not train:
				line += file_name_extension_separator

			line = line.replace('\n', '').split(file_name_extension_separator)
			for index, element in enumerate(line):
				is_numerical = False

				broken_up = element.replace(',', '.').split('.')
				if len(broken_up) <= 2:
					is_numerical = True
					is_negative = len(element) > 0 and element[0] == '-'
					element = element[1 if is_negative else 0:]
					for part in broken_up:
						if not part.isdecimal():
							is_numerical = False
							break

				if is_numerical:
					line[index] = float(('-' if is_negative else '') + element)

			output[1].append(line[0])
			output[2].append(line[1:-1])
			output[3].append(line[-1])
		output[0] = [output[1].pop(0)] + output[2].pop(0) + [output[3].pop(0)]

		variations = dict((feature_name, set()) for feature_name in output[0][1:-1])
		for house in output[2]:
			for index, feature in enumerate(house):
				if isinstance(feature, str):
					variations[output[0][index + 1]].add(feature)
				else:
					variations[output[0][index + 1]].add('A(slope)')
					# variations[output[0][index + 1]].add('B(slope)')

		output[4] = variations
	else:
		raise NotImplementedError

	return output
