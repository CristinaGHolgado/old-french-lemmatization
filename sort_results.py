import pandas as pd
import csv
pd.set_option('display.max_columns', None) 
import re


def sort_res(type):
	"""	DataFrame grouping tests results by lemmatizer
	
	Parameters
	----------
	type : str
		Unknown tokens ('inconnus'), all tokens ('tout')
	
	Returns
	-------
		DataFrame
	"""
	res_type = []
	with open(results_f, 'r', encoding='utf8') as f:
		file = f.read()[1:-1].replace("'","")
		list_res = [w for w in file.split(", ")]
		for item in list_res:
			if type in item:
				res_type.append(item)

	#	Results to df
	df = pd.DataFrame(res_type, columns = ['data'])
	df['test'] = df['data'].apply(lambda x: x.split("_")[3]).astype(int)
	df['tool'] = df['data'].apply(lambda x: x.split("_")[1])
	df['part'] = df['data'].apply(lambda x: x.split("_")[-2])
	df['precision'] = df['data'].apply(lambda x: x.split("_")[0])
	del df['data']

	lemmas_all = df.loc[df['part'] == 'Lemmas'].sort_values(by=['tool','test']).reset_index()
	lemmas_all['prec_lemmas'] = lemmas_all['precision'].astype(float)
	tags_all = df.loc[df['part'] == 'Tags'].sort_values(by=['tool','test']).reset_index()
	tags_all['prec_tags'] = tags_all['precision'].astype(float)
	lemtags_all = df.loc[df['part'] == 'TagLemma'].sort_values(by=['tool','test']).reset_index()
	lemtags_all['prec_lemtags'] = lemtags_all['precision'].astype(float)

	res_all = pd.concat([lemmas_all, tags_all, lemtags_all], axis=1)
	res_all['T'] = res_all.iloc[:,1]
	res_all['Lemmatiseur'] = res_all.iloc[:,2]
	del res_all['index']
	del res_all['test']
	del res_all['tool']
	del res_all['precision']
	del res_all['part']

	## All
	print(">> Ensemble des resultats")
	print(res_all)

	## Mean (avg all tests)
	print(">> Moyenne des tests")
	print(res_all.groupby(['Lemmatiseur'])['prec_lemmas','prec_tags','prec_lemtags'].mean().round(2))


results_f = 'raw_results.txt'	#	File contaning raw results

sort_res('tout')
sort_res('inconnus')


