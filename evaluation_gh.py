import csv
import glob
import os
import pandas as pd
pd.set_option('display.max_columns', 60)
import warnings
warnings.simplefilter(action='ignore')
from sklearn import metrics
from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support
import numpy as np
import re
import sys
sys.stdout = open('Resultats.txt','w')


def evaluation_cc_annotes(merge=None):
	"""
	"""
	def merge_corpus_annotes():
		for dir in glob.glob("*\\*\\CC_annotes\\*merged*"):
			try:
				"""
				supprimer le fichier qui contient chache cc annote fusione car lorsuq'on relance la concatenation, celui ci, s'il existe deja, s'ajoute a la concatenation.
				"""
				os.remove(dir)
			except:
				print("Error while deleting file ", filePath)

		for dir in glob.glob("*\\*\\CC_annotes"):
			nomsortie = dir+"\\cc_annotes_merged.csv"
			files = glob.glob(os.path.join(dir,"*"))
			df_cc = pd.concat([pd.read_csv(f, sep='\t',header=None, encoding='utf8', quoting=csv.QUOTE_NONE, dtype=object) for f in files], axis=1)
			df_cc.to_csv(nomsortie, sep='\t', encoding='utf8', header=None,index=False)
	
	if merge == True:
		merge_corpus_annotes()

	for dir in glob.glob("*\\*\\CC_annotes\\*merged*"):
		testname = dir.split('\\')[1]
		df = pd.read_csv(dir, sep='\t', encoding='utf8', names=['forme_lg','tag_lg','lemme_lg','nb','nb2','forme_nlp','lemme_nlp','forme_nlpp','tag_nlp','gold_f','gold_cattex','gold_ud','gold_lemme','tt_forme_u','tt_tag_u','tt_lemme_u','tt_forme','tt_tag','tt_lemme','udpipe_forme','udpipe_lemme','udpipe_upos','udpipe_tag','udpipe_morphinfo'], quoting=csv.QUOTE_NONE, dtype=object)
		df = df[['gold_f','gold_cattex','gold_lemme','tt_tag','tt_lemme','tt_tag_u','tt_lemme_u','tag_lg','lemme_lg','udpipe_tag','udpipe_lemme','tag_nlp','lemme_nlp']]
		df = df.dropna()
		df = df[~df['gold_lemme'].str.contains('no_lem')]
		df = df[~df.gold_cattex.str.contains('NOMpro')]
		df = df[~df.gold_cattex.str.contains('PON')]
# /////////////
# PRETRAITEMENT
# ////////////

		## pretraitement lemmes UDPIPE
		df['udpipe_lemme'] = df['udpipe_lemme'].str.replace('\d+', '')
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

		## fill nans
		df['udpipe_lemme'] = df['udpipe_lemme'].fillna('None')
		df['udpipe_tag'] = df['udpipe_tag'].fillna('None')

		print(testname,'\n============================================================')
# /////////////
# EVALUATION
# ////////////

		def liste(coln):
			return [str(x) for x in coln.values]
		def precision(gold,pred):
			return [round(metrics.precision_score(gold, pred, average='micro'),2)]

# LEMMES
#
		def ev_lemmes():
			lems = df[['gold_f','gold_lemme','udpipe_lemme','lemme_lg','tt_lemme','tt_lemme_u','lemme_nlp','tag_lg']] # tag_lg aussi pour le pretraitement

			# # lemmes
			lem_gold = liste(lems.gold_lemme)
			lem_ud, lem_lg, lem_tt, lem_nlp = liste(lems.udpipe_lemme), liste(lems.lemme_lg), liste(lems.tt_lemme), liste(lems.lemme_nlp)

			prec_tt = precision(lem_gold,lem_tt)
			prec_udpipe = precision(lem_gold,lem_ud)
			prec_nlp = precision(lem_gold,lem_nlp)
			prec_lg = precision(lem_gold,lem_lg)

			## precision LGERM 	
				# - (si lem gold dans lem lgerm)
			lems['lemmes_commun'] = lems.apply(lambda x: str(x.gold_lemme) in str(x.lemme_lg), axis=1).astype(str)
			lems.loc[lems['lemmes_commun'].astype(str).str.contains('True'), 'lemmes_commun'] = lems['gold_lemme']
			lg_lem_in_gold = [str(lem) for lem in lems.lemmes_commun.values]
			prec_lg_2 = round(metrics.precision_score(lem_gold, lg_lem_in_gold, average='micro'),2)
			rappel_lg_2 = round(metrics.recall_score(lem_gold, lg_lem_in_gold, average='micro'),2)
			false_lgerm = lems[lems.lemmes_commun != lems.gold_lemme]
			erreurs = false_lgerm[['gold_f','gold_lemme','lemme_lg']]
			n = dir.replace('cc_annotes_merged.csv','erreurs_lgerm.csv')
			erreurs.to_csv(n, sep='\t', encoding='utf8')
				
				# - (si lem gold dans lem lgerm = 1 / nb lemmes proposes)
			df_tt_lgerm = lems[['gold_lemme','lemme_lg']]
			# ignorer contractions (dans ce cas, il faut tenir compte de la cellule en entier)
			df_tt_lgerm.loc[df_tt_lgerm.lemme_lg.str.contains(contractions), 'lemme_lg'] = df_tt_lgerm.lemme_lg.str.replace('##','--')
			# definir scores a 0
			df_tt_lgerm['scores'] = '0'
			# Si le lemme gold apparait dans les lemmes proposes (il ne peut avoir qu'une occurrence, car il n'y a qu'un lemme dans la cl==colonne gold_lemme)
			df_tt_lgerm.loc[df_tt_lgerm.apply(lambda x: str(x.gold_lemme) in str(x.lemme_lg), axis=1), 'scores'] = 1
			# pur ces cellules ou il y a plusieurs lemmes (caracteries par la presence de # qui separe les lemmes), 1/(nombre_lemmes/1)  --  Le +1 a la fin c'est pour additioner a partir de 1 (sinon, s'il y a 3 lemmes ou 1 correcte, il donne 0.5 ay lieu de 0.333)
			df_tt_lgerm.loc[(df_tt_lgerm['lemme_lg'].str.contains("#")), 'scores'] = 1/(df_tt_lgerm['lemme_lg'].str.count("##")+1)
			## remettre a 0 les scores pour les celulles de la colonne lemme_lg si aucun des lemmes proposes est dans la colonne gold_lemme
			df_tt_lgerm.loc[~df_tt_lgerm.apply(lambda x: str(x.gold_lemme).lower() in list(x.lemme_lg.split('##')), axis=1) & (df_tt_lgerm.lemme_lg.str.contains('##')), 'scores'] = 0
			resultat_tt_lgerm = round(df_tt_lgerm.scores.astype(int).sum(axis = 0)/len(df_tt_lgerm.scores), 2)

			print("LEMMES =  TREETAGGER : ",prec_tt, " UDPIPE : ", prec_udpipe, " NLP-PIE : ",prec_nlp, "LGERM : ", resultat_tt_lgerm)

		ev_lemmes() 


# # #
# # ETIQUETTES
# # #

		def ev_etiquettes():

			tags = df[['gold_cattex','udpipe_tag','tag_lg','tt_tag','tag_nlp']]

			gold_tag, tag_udpipe, tag_lgerm, tag_ttagger, tag_nlpp = liste(tags.gold_cattex), liste(tags.udpipe_tag), liste(tags.tag_lg), liste(tags.tt_tag), liste(tags.tag_nlp)
			prec_ud, prec_lg, prec_tt, prec_nlp = precision(gold_tag, tag_udpipe), precision(gold_tag, tag_lgerm), precision(gold_tag, tag_ttagger), precision(gold_tag, tag_nlpp)
			print("ETIQUETTES =  TREETAGGER : ",prec_tt, " UDPIPE : ", prec_ud, " NLP-PIE : ",prec_nlp, "LGERM : ", prec_lg)
		ev_etiquettes()
	
# #
# #-- ETIQUETTES ET LEMMES
# #
		def etiquette_et_lemme():
			# gold lemme + gold cattex | pred lemme + pred etiquette
			gold_merged = df[['gold_cattex','gold_lemme']].agg(' '.join, axis=1)
			lg_merged = df[['tag_lg','lemme_lg']].agg(' '.join, axis=1)
			ud_merged= df[['udpipe_tag','udpipe_lemme']].agg(' '.join, axis=1).astype(str)
			tt_merged = df[['tt_tag','tt_lemme']].agg(' '.join, axis=1)
			nlp_merged = df[['tag_nlp','lemme_nlp']].agg(' '.join, axis=1)

			gold_taglem = liste(gold_merged)
			lg_taglem = liste(lg_merged)
			tt_taglem = list(tt_merged)
			ud_taglem = list(ud_merged)
			nlp_taglem = list(nlp_merged)

			prec_lg = precision(gold_taglem, lg_taglem)
			prec_ud = precision(gold_taglem, ud_taglem)
			prec_tt = precision(gold_taglem, tt_taglem)
			prec_nlp = precision(gold_taglem, nlp_taglem)
			print("ETIQUETTE ET LEMME =  TREETAGGER : ",prec_tt, " UDPIPE : ", prec_ud, " NLP-PIE : ",prec_nlp, "LGERM : ", prec_lg)
		
		etiquette_et_lemme()


# #
# #-- LEMMES PAR CATEGORIE
# #

		def lemme_par_et():
			print('EVALUATION PAR ETIQUETTE\n------------------------\n')
			print('- UDPIPE : \n')
			lem_true_ud = df.groupby('gold_cattex', sort=False).apply(lambda g: len(g[g.gold_lemme == g.udpipe_lemme]))
			lem_false_ud = df.groupby('gold_cattex', sort=False).apply(lambda g: len(g[g.gold_lemme != g.udpipe_lemme]))
			res_lem_cat_ud = round(lem_true_ud/(lem_true_ud+lem_false_ud),2)
			res = res_lem_cat_ud.to_frame(name = 'score').reset_index().sort_values(by='score', ascending=False)
			# LGERM
			print("- LGERM : \n")
			lem_true_lg = df.groupby('gold_cattex', sort=True).apply(lambda g: len(g[g.gold_lemme == g.lemme_lg]))
			lem_false_lg = df.groupby('gold_cattex', sort=True).apply(lambda g: len(g[g.gold_lemme != g.lemme_lg]))
			res_lem_cat_lg = round(lem_true_lg/(lem_true_lg+lem_false_lg),2)
			res['lgerm'] = res_lem_cat_lg.to_frame(name = 'score_lg').reset_index().sort_values(by='score_lg', ascending=False)
			print(res)
		
		lemme_par_et()


evaluation_cc_annotes(merge=False)
