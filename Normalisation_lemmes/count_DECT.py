import pandas as pd
import csv
import glob
import os


def count(corpus_path):
	"""
	Calcul de la proportion de lemmes non normalisés avec regroupement par étiquettes.

	Parametres
	----------
	corpus_path : str
		Chemin vers les fichiers normalisés du corpus
	
	Sortie
	------
		file object
	"""
	files = glob.glob(os.path.join(corpus_path,"*.conllu"))
	for f in files:
		name = f.split('//')[-1].replace('corpus_normalise\\','')
		name = name.replace("normalise(lemmes_corriges)_dect_en_dmf","")
		print(name,'\n================')
		corpus = pd.read_csv(f, sep='\t', encoding='utf-8',
			names=['forme', "lemme", "pos", "cattex", "imorph1", "imorph2","imorph3",'imorph4','src'],
			quoting=csv.QUOTE_NONE,
			dtype='object')

		taille_corpus = len(corpus)
		print("Taille corpus : ", taille_corpus)
		non_normalises = corpus[~corpus.src.str.contains('DMF')]
		print('Nombre lemmes non normalises : ', len(non_normalises),"(", round((len(non_normalises)*100)/taille_corpus,3)," % du corpus)")
		non_norm_cont_punct = non_normalises[non_normalises.cattex.str.contains('PON')]
		print("Nombre de lemmes non normalises qui sont ponctuation :", len(non_norm_cont_punct),"(",round((len(non_norm_cont_punct)*100)/len(non_normalises),3)," % du total des nombres des lemmes non normalises)")
		print("Nombre de lemmes non normalises sans ponctuation :", len(non_normalises)-len(non_norm_cont_punct))
		print()
		print("Nombre de lemmes non normalises par etiquette :")
		categories = non_normalises[~non_normalises['cattex'].str.contains('PON')].groupby(['cattex']).size().sort_values(ascending=False)
		print(categories)

		nombre_normalises = len(corpus[corpus.src.str.contains('DMF')]) # lemmes qui contienent DMF
		pourcentage_norm = round(nombre_normalises*100/taille_corpus,2)
		nombre_DECT = len(corpus[~corpus.src.str.contains('DMF')]) # lemmes qui ne contiennent pas DMF
		pourcentage_dect = round(nombre_DECT*100/taille_corpus,2)
		dect = corpus[~corpus.src.str.contains('DMF')]
		ponctuation = dect[~dect['cattex'].str.contains('PON')]
		total_sans_ponct = len(ponctuation)


		df_simplifie = ponctuation
		df_simplifie['common'] = ponctuation[['lemme','cattex']].agg(' '.join, axis=1)
		df_simplifie = df_simplifie.drop_duplicates(subset=['common'], keep='first')
		del df_simplifie ['common']
		fname_no_duplicates = "dect_restants\\no_duplicates"+name
		df_simplifie.to_csv(fname_no_duplicates, encoding='utf8', sep='\t', header=False)

		total_no_rempl = len(dect) - len(dect[dect.cattex.str.contains('PON')]) # ni tienent DMF ni estos despues son PONC
		cats = ponctuation[~ponctuation['cattex'].str.contains('PON')].groupby(['cattex']).size().sort_values(ascending=False)

		fname = "dect_restants\\"+name.replace('tldmf_output_dect_en_dmf','dect_restants(sans_ponct)')
		ponctuation.to_csv(fname, encoding='utf8', sep='\t', header=False)

count('corpus_normalise')