#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import csv
import glob
import os
pd.set_option('display.max_columns', 60)
import warnings
warnings.simplefilter(action='ignore')
from sklearn import metrics
from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support
import re
import sys

def comb_lemme():
	for dir in glob.glob("*\\*\\CC_annotes\\*merged*"):
		testname = dir.split('\\')[1]
		df = pd.read_csv(dir, sep='\t', encoding='utf8', names=['forme_lg','tag_lg','lemme_lg','nb','nb2','forme_nlp','lemme_nlp','forme_nlpp','tag_nlp','gold_f','gold_cattex','gold_ud','gold_lemme','tt_forme_u','tt_tag_u','tt_lemme_u','tt_forme','tt_tag','tt_lemme','udpipe_forme','udpipe_lemme','udpipe_upos','udpipe_tag','udpipe_morphinfo'], quoting=csv.QUOTE_NONE, dtype=object)
		df = df[['gold_f','gold_cattex','gold_lemme','tt_tag','tt_lemme','tt_tag_u','tt_lemme_u','tag_lg','lemme_lg','udpipe_tag','udpipe_lemme','tag_nlp','lemme_nlp']]

		## pretraitement lemmes UDPIPE
		df['udpipe_lemme'] = df['udpipe_lemme'].str.replace('\d+', '')
		df.loc[df['udpipe_tag'].eq('NOMpro') , 'udpipe_lemme'] = df['udpipe_lemme'].str.capitalize()
		## pretraitement nlp-pie
		df['lemme_nlp'] = df['lemme_nlp'].str.lower()
		df.loc[df['tag_nlp'].eq('NOMpro') , 'lemme_nlp'] = df['lemme_nlp'].str.capitalize()
		# pretraitement lemmes LGERM
		df['lemme_lg'] = df['lemme_lg'].str.replace('_mot_inconnu', '<unknown>')
		df['lemme_lg']= df['lemme_lg'].str.lower()
		mi = re.compile(r"^µ")
		df['lemme_lg'] = [mi.sub('', str(x)) for x in df['lemme_lg']]
		df.loc[df['tag_lg'].eq('NOMpro') , 'lemme_lg'] = df['lemme_lg'].str.capitalize()
		df['lemme_lg'] = df['lemme_lg'].str.replace('\d+', '')
		df['lemme_lg'] = [x.replace('##',".") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace('|',"##") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("le##à","à.le") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("en##le","en.le") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("le##de","de.le") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("de##le","de.le") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("je##le","je.le") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("ne##le","ne.le") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("ledit##à","à.ledit") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("lequel##à","à.lequel") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("le##que","que.le") for x in df['lemme_lg']]
		df['lemme_lg'] = [x.replace("_","") for x in df['lemme_lg']]
		contractions = r'^de\.le$|^de\.les$|^a\.les$|^a\.le$|^le\.à$|^à\.les$|^à\.le$|^de\.lequel$|^de\.lequel$|^je\.le$|^ne\.le$|^à\.lequel$|^à\.ledit$|^que\.le$|^en\.le$'

		print(testname,'\n============================================================')

	## choix des lemmes
		lemmes = df[['lemme_lg','udpipe_lemme','tt_lemme','lemme_nlp']]
		lemmes['comb_lemme'] = lemmes[lemmes.columns[0:]].apply(lambda x: '#'.join(x.dropna().astype(str)), axis=1)
		lemmes['lemme'] = df['lemme_lg']
		lemmes['comb_lemme'] = lemmes['comb_lemme'].str.replace('##','#')
		lemmes['comb_lemme'] = lemmes['comb_lemme'].str.lower()
		lemmes['lemme'] = [list(duplicates(str(x).split('#'))) for x in lemmes['comb_lemme']]
		lemmes['lemme'] = ['#'.join(x).split('#')[0] for x in lemmes['lemme']]
		lemmes.loc[lemmes["lemme"]=='','lemme'] = lemmes.lemme_lg.map(lambda x: x.split('#')[0])

	## choix des etiquettes
		tags = df[['tag_lg','udpipe_tag','tt_tag','tag_nlp']]
		tags['comb_tags'] = tags[tags.columns[0:]].apply(lambda x: '#'.join(x.dropna().astype(str)), axis=1)
		tags['tag'] = df['tag_lg']
		tags['tag'] = [list(duplicates(str(x).split('#'))) for x in tags['comb_tags']]
		tags['tag'] = ['#'.join(x).split('#')[0] for x in tags['tag']]
		tags.loc[tags["tag"]=='','tag'] = tags["tag_lg"]
		lem_et_tag = pd.concat([df.gold_f, df.gold_cattex, df.gold_lemme, lemmes.lemme, tags.tag], axis=1)
		lem_et_tag.loc[lem_et_tag['tag'].eq('NOMpro') , 'lemme'] = lem_et_tag['lemme'].str.capitalize()
		print(lem_et_tag)
		
		fname= dir.replace('cc_annotes_merged2.csv','comb_lemmatiseurs.csv')
		lem_et_tag.to_csv(fname, encoding='utf8', sep='\t', header=None, index=False)

	
					
def evaluation():
	for dir in glob.glob("*\\*\\CC_annotes\\*comb_*"):
		df_cc = pd.read_csv(dir, sep='\t', encoding='utf8', names=['gold_f','gold_cattex','gold_lemme','lemme','tag'], quoting=csv.QUOTE_NONE, dtype=object)
		df_cc = df_cc[~df_cc.gold_cattex.str.contains('NOMpro')]
		df_cc = df_cc[~df_cc.gold_cattex.str.contains('PON')]
		lemmes_gold = [str(lem) for lem in df_cc.gold_lemme.values]
		lemmes_com = [str(lem) for lem in df_cc.lemme.values]
		prec_comb = round(metrics.precision_score(lemmes_gold, lemmes_com, average='micro'),2)
		print(dir)
		print("Lemmes :", prec_comb)

		t_gold = [str(t) for t in df_cc.gold_cattex.values]
		t_com = [str(t) for t in df_cc.tag.values]
		prec_comb2 = round(metrics.precision_score(t_gold, t_com, average='micro'),2)
		print("cattex: ", prec_comb2)

		lem_et_gold = df_cc[['gold_cattex', 'gold_lemme']].agg(' '.join, axis=1)
		lem_et_pred = df_cc[['tag', 'lemme']].astype(str).agg(' '.join, axis=1)
		gold_etlem = [str(t) for t in lem_et_gold.values]
		pred_etlem = [str(t) for t in lem_et_pred.values]
		prec_etlem = round(metrics.precision_score(gold_etlem, pred_etlem, average='micro'),2)
		print(prec_etlem)
		print()
comb_lemme()
evaluation()

