import pandas as pd
import csv
import subprocess
import re



def split(file, percentage_nb):
	''' Split input file into train/dev at choosen dev percentage

	Parameters
	----------
	file :	str
		input corpus (conLL-U format)

	percentage_nb : int
		% of input training corpus to be splitted as dev set
	'''
	
	split_index = []

	with open(file, "r", encoding="utf8") as f:
		
		corpus = f.readlines()
		sents_index = []
		
		for i, line in enumerate(corpus):

			if line.startswith("# sent_id"):

				sents_index.append(i) # append sentence id when sent_id in file
		

		dict_indexes = dict(zip(sents_index,[sents_index.index(i) for i in sents_index]))
		
		split_at = round((percentage_nb*len(sents_index))/100)+1 # split at sentence id (10% of the sentences to devset)
		
		split_from_line = list(dict_indexes.items())[-split_at:][0][0]
		split_index.append(split_from_line)


		print(f"File length: {len(corpus)}")
		print(f"Sentences (`sent_id` count) in file: {len(sents_index)}")


	filename = list(filter(None, re.split(r"\.conllu|\\", file)))[-1]

	# split corpus file from firt line to choosen index-1 as train set
	subprocess.check_output(['bash','-c', f"head -n {split_index[0]-1} {file} > {filename + '.conllu'}"])
	#  split corpus file from choosen index to end dev set
	subprocess.check_output(['bash','-c', f"tail -n +{split_index[0]} {file} > {filename + '_dev.conllu'}"])


### split(corpus_file, 10) # use 10% for dev from input training file
