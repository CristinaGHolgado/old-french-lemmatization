import pandas as pd
import csv
import glob
import os
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
import warnings
warnings.simplefilter(action='ignore')
from sklearn import metrics
from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support
import numpy as np
import re
import sys

import merge_lemmatized

import preprocess_lemmatized
from preprocess_lemmatized import preprocess



def liste(coln):
	return [str(x) for x in coln.values]

def precision(gold, pred):
	return [round(metrics.precision_score(gold, pred, average='micro'),2)]	


def errors(df, eval=None):
	''' If eval True return precision
	'''

	def getErrors(df, tool, lemme_col, tag_col, unknown=None, lgerm=None):

		print(f"\n====> {tool.upper()}\n")
		unknown_val = []
		
		if unknown == True:
			unknown_val.append('inconnus')
			print("*** Selection d'erreurs sur les tokens inconnus ***\n")
			df = df[df.tt_lemme_u == '<unknown>']	#	Select <unknown> rows ( = lemmas not in traning set)
		else:
			unknown_val.append('tout')
			print("*** Selection de tous les tokens ***\n")
			df = df

		fileOutName = (f"ErreursLemmes/{testname}_erreurs_{unknown_val}_{tool}_")

		if tool.lower() != 'lgerm':
			
			#	Erreurs lemmes
			err_lems = df[['gold_f','gold_lemme','gold_cattex', 'tt_lemme_u', lemme_col, tag_col]][df.gold_lemme != df[lemme_col]]
			
			err_lems.to_csv(str(fileOutName+"lemmes.csv"),sep='\t', encoding='utf8', quoting = csv.QUOTE_NONE)
			print("\n[[LEMMES]]")
			res_lemmes = precision(liste(df.gold_lemme), liste(df[lemme_col]))
			print('- Precision = ', res_lemmes if eval == True else None)

			id_lemmes = str(res_lemmes[0]) + "_" + tool + "_" + str(testname) + "_Lemmas_" + str(unknown_val[0])
			precision_lemmatiseurs.append(id_lemmes)


			#	Erreurs etiquetes
			err_tags = df[['gold_f','gold_lemme','gold_cattex', 'tt_lemme_u', lemme_col, tag_col]][df.gold_cattex != df[tag_col]]
			
			err_tags.to_csv(str(fileOutName+"etiquettes.csv"), sep='\t', encoding='utf8', quoting = csv.QUOTE_NONE)
			print("\n[[ETIQUETTES]]")
			res_tags = precision(liste(df.gold_cattex), liste(df[tag_col]))
			print('- Precision = ', res_tags if eval == True else None)

			id_tags = str(res_tags[0]) + "_" + tool + "_" + str(testname) + "_Tags_" + str(unknown_val[0])
			precision_lemmatiseurs.append(id_tags)

			#	Erreurs et/lem
			tagLem = df[['gold_f','gold_lemme','gold_cattex', 'tt_lemme_u',lemme_col, tag_col]]
			
			tagLem[f'{tool}_tag_lemma'] = tagLem[[lemme_col, tag_col]].agg('_'.join, axis=1)
			tagLem['gold_tag_lemma'] = tagLem[['gold_lemme', 'gold_cattex']].agg('_'.join, axis=1)
			
			tagLem_err = tagLem[tagLem[f"{tool}_tag_lemma"] != tagLem['gold_tag_lemma']]
			
			tagLem_err.to_csv(str(fileOutName+"lemmes&etiquettes.csv"), sep='\t', encoding='utf8', quoting = csv.QUOTE_NONE)
			print("\n[[ETIQUETTES ET LEMMES]]\n")
			res_tag_lem = precision(liste(tagLem['gold_tag_lemma']), liste(tagLem[f'{tool}_tag_lemma']))
			print('- Precision = ', res_tag_lem if eval == True else None)
			
			id_taglem = str(res_tag_lem[0]) + "_" + tool + "_" + str(testname) + "_TagLemma_" + str(unknown_val[0])
			precision_lemmatiseurs.append(id_taglem)


		if 'lgerm' in tool.lower():		#	LGeRM is evaluated differently as it provides all possible lemmas for a token
			# Lemmes
				##	Lemmes (si lemme gold <> lemme dans lgerm = 1)
			df_lgerm = df[['gold_f', 'gold_lemme', 'gold_cattex', lemme_col, tag_col]]
			
			df_lgerm['lemmes_commun'] = df_lgerm.apply(lambda x: str(x.gold_lemme) in str(x.lemme_lg), axis=1).astype(str)
			df_lgerm.loc[df_lgerm['lemmes_commun'].astype(str).str.contains('True'), 'lemmes_commun'] = df_lgerm['gold_lemme']
			df_err = df_lgerm.loc[df_lgerm.lemmes_commun != df_lgerm.gold_lemme]
			res_lemmes1 = str(precision(liste(df_lgerm['gold_lemme']), liste(df_lgerm['lemmes_commun']))[0]) + "_" + tool
			print('- Precision (si gold dans lgerm) = ', res_lemmes1 if eval == True else None)
				
				##	Lemmes (si lemme gold <> lemme dans lgerm = 1/(nb lemmes proposes par lgerm))
			df_lgerm['scores'] = '0'	#	Start at 0
			# Si le lemme gold apparait dans les lemmes proposes (il ne peut avoir qu'une occurrence, car il n'y a qu'un lemme dans la cl==colonne gold_lemme)
			df_lgerm.loc[df_lgerm.apply(lambda x: str(x.gold_lemme) in str(x.lemme_lg), axis=1), 'scores'] = 1
			# pur ces cellules ou il y a plusieurs lemmes (caracteries par la presence de # qui separe les lemmes), 1/(nombre_lemmes/1)  --  Le +1 a la fin c'est pour additioner a partir de 1 (sinon, s'il y a 3 lemmes ou 1 correcte, il donne 0.5 ay lieu de 0.333)
			df_lgerm.loc[(df_lgerm['lemme_lg'].str.contains("#")), 'scores'] = 1/(df_lgerm['lemme_lg'].str.count("##")+1)
			## remettre a 0 les scores pour les celulles de la colonne lemme_lg si aucun des lemmes proposes est dans la colonne gold_lemme
			df_lgerm.loc[~df_lgerm.apply(lambda x: str(x.gold_lemme).lower() in list(x.lemme_lg.split('##')), axis=1) & (df_lgerm.lemme_lg.str.contains('##')), 'scores'] = 0
			res_lemmes2 = [round(df_lgerm.scores.astype(int).sum(axis = 0)/len(df_lgerm.scores), 2)]
			print('- Precision (si gold dans lgerm/nb lemmes lgerm) = ', res_lemmes2 if eval == True else None)

			id_lemmes_lgerm = str(res_lemmes2[0]) + "_" + tool + "_" + str(testname) + "_Lemmas_" + str(unknown_val[0])
			precision_lemmatiseurs.append(id_lemmes_lgerm)

			#	Etiquettes
			lgTag = df_lgerm[df_lgerm.gold_cattex != df_lgerm[tag_col]]
			res_tags_lgerm = precision(liste(df_lgerm['gold_cattex']), liste(df_lgerm[tag_col]))
			print('- Precision (etiquettes) = ', res_tags_lgerm if eval == True else None)
			id_tags_lgerm = str(res_tags_lgerm[0]) + "_" + tool + "_" + str(testname) + "_Tags_" + str(unknown_val[0])
			precision_lemmatiseurs.append(id_tags_lgerm)

			#	Et/Lemme
			df_lgerm['gold_taglem'] = df_lgerm['gold_lemme'] + "_" + df_lgerm['gold_cattex']
			df_lgerm['lg_taglem'] = df_lgerm['lemmes_commun'] + "_" + df_lgerm[tag_col]
			err_lg_taglem = df_lgerm.loc[df_lgerm[tag_col] != df_lgerm['gold_taglem']]
			res_taglem_lgerm = precision(liste(df_lgerm['gold_taglem']), liste(df_lgerm['lg_taglem']))
			print('- Precision (etiq/lemmes) = ', res_taglem_lgerm if eval == True else None)

			id_taglem_lgerm = str(res_taglem_lgerm[0]) + "_" + tool + "_" + str(testname) + "_TagLemma_" + str(unknown_val[0])
			precision_lemmatiseurs.append(id_taglem_lgerm)
			
			del df_lgerm['lemmes_commun']
			del df_lgerm['lg_taglem']
			del df_lgerm['gold_taglem']

			df_err.to_csv(str(fileOutName+"lemmes.csv"), sep='\t', encoding='utf8', quoting = csv.QUOTE_NONE)
			lgTag.to_csv(str(fileOutName+"lemmes.csv"), sep='\t', encoding='utf8', quoting = csv.QUOTE_NONE)
			err_lg_taglem.to_csv(str(fileOutName+"lemmes.csv"), sep='\t', encoding='utf8', quoting = csv.QUOTE_NONE)



	getErrors(df, "PIE", "lemme_nlp", "tag_nlp")
	getErrors(df, "UDPIPE", "udpipe_lemme", "udpipe_tag")
	getErrors(df, "TREETAGGER", "tt_lemme", "tt_tag")
	getErrors(df, "LGERM", "lemme_lg", "tag_lg")

	getErrors(df, "PIE", "lemme_nlp", "tag_nlp", unknown=True)
	getErrors(df, "UDPIPE", "udpipe_lemme", "udpipe_tag", unknown=True)
	getErrors(df, "TREETAGGER", "tt_lemme", "tt_tag", unknown=True)
	getErrors(df, "LGERM", "lemme_lg", "tag_lg", unknown=True)



##############################################################

files_path = "*\\*\\CC_annotes\\*merged*"	#	Path to tests folders with merged lemmatized corpus
ignore_tags = ['NOMpro','PON*','OUT']	#	Tags to ignore from evaluation
precision_lemmatiseurs = []	#	Store results for all tokens & unknown tokens

# if __name__ == 'main':
for dir in glob.glob(files_path):
	testname = dir.split('\\')[1]	#	Tests name
	print("\n\n***********************************************")
	print(testname)
	print("*************************************************\n")

	data_lemmatized = preprocess_lemmatized.preprocess(dir, testname, unknown=False, ignore_tags=ignore_tags)	#	Run preprocess of tagged files
	errors(data_lemmatized, eval=True)	#	Return errors and evaluation

with open("raw_results.txt", 'w', encoding='utf8') as f:
	f.write(str([''.join(w) for w in precision_lemmatiseurs]))
	f.close()

