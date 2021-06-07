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


def preprocess(file, test_name, unknown=None, ignore_tags=None):
	"""Prepare corpus for evaluation into a single dataframe
	"""
	testname = test_name

	df = pd.read_csv(file, sep='\t', encoding='utf8', names=['forme_lg','tag_lg','lemme_lg','nb','nb2','forme_nlp','lemme_nlp','forme_nlpp','tag_nlp','gold_f','gold_cattex','gold_ud','gold_lemme','tt_forme_u','tt_tag_u','tt_lemme_u','tt_forme','tt_tag','tt_lemme','udpipe_forme','udpipe_lemme','udpipe_upos','udpipe_tag','udpipe_morphinfo'], quoting=csv.QUOTE_NONE, dtype=object)
	df = df[0:500]
	#	Select columns
	df = df[['gold_f','gold_cattex','gold_lemme','tt_tag','tt_lemme','tt_tag_u','tt_lemme_u','tag_lg','lemme_lg','udpipe_tag','udpipe_lemme','tag_nlp','lemme_nlp']]

	# ignore empty rows in df if empty values in gold_lemme
	df = df[~df['gold_lemme'].str.contains('no_lem')]
	df = df.replace(np.nan, 'no_lemme', regex=True)

	
	print()
	
	print("- Nombre de tokens : ", len(df))

	if unknown == True:
		df_unknown = df[df.tt_lemme_u == '<unknown>']
		print(f"- Nombre de tokens inconnus : {len(df_unknown)} ({(len(df_unknown)*100)/len(df)}%)")
		print("Categories auxquelles appartiennent les tokens inconnus : \n", df.groupby('gold_cattex')['gold_cattex'].apply(lambda x: int(((x.count())/len(df))*100)).reset_index(name='count').sort_values(['count'], ascending=False))
		df = df_unknown
	else:
		pass


	if len(ignore_tags) >= 1:
		df = df[~df.gold_cattex.str.contains('|'.join(ignore_tags))]
	else:
		pass


	# Preprocessing

	## Lemmas UDPIPE
	df['udpipe_lemme'] = df['udpipe_lemme'].str.replace('\d+', '')	# Remove digits on lemmas
	df['udpipe_lemme'] = df['udpipe_lemme'].fillna('None')	#	Fill nan values
	df['udpipe_tag'] = df['udpipe_tag'].fillna('None')
	
	## Lemmas PIE
	df['lemme_nlp'] = df['lemme_nlp'].str.lower()	# Lower lemmas
	df.loc[df['gold_cattex'].eq('NOMpro') , 'lemme_nlp'] = df['lemme_nlp'].str.capitalize()	#	Capitalize Pie proper nouns based if gold lemma is a proper noun
	df.loc[df.gold_cattex != 'NOMpro', 'lemme_nlp'] = df['lemme_nlp'].str.lower()
	
	## Lemmas LGERM
	inconnus_lgerm = df[df.lemme_lg.str.contains("_")]	#	Unknown tokens unique to LGeRM (they start by `_`)
	print(f"Nombre de mots inconnus de LGeRM : {len(inconnus_lgerm)}")

	df['lemme_lg']= df['lemme_lg'].str.lower()	#	Lower lemmas
	df['lemme_lg'] = df['lemme_lg'].str.replace(r'^_mot.*', '<unknown>')	# Convert lgerm unknown tag to gold <unknown> tag
	df['lemme_lg'] = df['lemme_lg'].str.replace("_","")	#	Remove `_` from lemmas (= external lemmas to lgerm)

	mi = re.compile(r"^µ")
	df['lemme_lg'] = [mi.sub('', str(x)) for x in df['lemme_lg']]
	df.loc[df['tag_lg'].eq('NOMpro') , 'lemme_lg'] = df['lemme_lg'].str.capitalize()	#	Capitalize proper nouns
	df['lemme_lg'] = df['lemme_lg'].str.replace('\d+', '')	#	Remove digits from lemmas
	df['lemme_lg'] = [x.replace('|',"##") for x in df['lemme_lg']]	#	FORMS :  de|le > de#le  // sous|sus > sous##sous


	format_lg_to_gold = {"le##à":"à.le",	#	Process comp. grammar forms&format to gold lemme format(le##ne > ne.le, de##le > de.le, etc.)
							"en##le":"en.le",
							"le##de":"de.le",
							"de##le":"de.le",
							"je##le":"je.le",
							"ne##le":"ne.le",
							"ledit##à":"à.ledit",
							"lequel##à":"à.lequel",
							"le##que":"que.le"}
	
	dic = {r"\b{}\b".format(k): v for k, v in format_lg_to_gold.items()}
	df['lemme_lg'] = df['lemme_lg'].replace(dic, regex=True)

			### Capitaliser les lemmes lgerm si le lemme gold est NOMpro, dans le cas ou lgerm fourni plusieurs lemmes (Lucan##Lucain)
	df.loc[df.gold_cattex.str.contains("NOMpro"), 'nompro_lgerm_gold'] = df.lemme_lg.apply(lambda x: [mot.capitalize() for mot in x.split("##") if "##" in x])
	df.loc[df['nompro_lgerm_gold'].isna(), 'nompro_lgerm_gold'] = ""
	df.loc[df['nompro_lgerm_gold'].str.len() == 0, 'nompro_lgerm_gold'] = ""
	df.gold_lemme = df.gold_lemme.str.replace(" ","")
	df['nompro_lgerm_gold'] = df['nompro_lgerm_gold'].apply(lambda x: ' '.join(x))
	df['nompro_lgerm_gold'] = df.apply(lambda x: str(x.gold_lemme) in str(x.nompro_lgerm_gold), axis=1).astype(str)
	df.loc[df.nompro_lgerm_gold.astype(str).str.contains("True"), "lemme_lg"] = df['gold_lemme']
	del df['nompro_lgerm_gold']

	contractions = r'^de\.le$|^de\.les$|^a\.les$|^a\.le$|^le\.à$|^à\.les$|^à\.le$|^de\.lequel$|^de\.lequel$|^je\.le$|^ne\.le$|^à\.lequel$|^à\.ledit$|^que\.le$|^en\.le$'

	##	All lemmas
	df = df.replace('œ', 'oe', regex=True)	#	Replace all 'œ' to 'oe' as some lemmatizers display it different in certain words
	

	##	Insert file name to first row
	df[testname] = ''

	return df
