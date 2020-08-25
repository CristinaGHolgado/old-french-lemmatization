import pandas as pd
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows',3000)
import csv
import re
import numpy as np
import time
import glob
import os
import pathlib



def udpipe_mid_files():
	"""
	Creation des dossiers pour les fichiers de sortie :
		- Fichiers intermediaires
		- Corpus pour UDPIPE
	"""
	try:
		os.makedirs('udpipe_f_intermediaires')
	except FileExistsError:
		pass


def make_id_texte():
	for dir in glob.glob("*\\*\\CORPUS_APPRENTISSAGE"):
		files = glob.glob(os.path.join(dir,"*.conllu"))
		df = pd.concat([pd.read_csv(f, sep='\t', encoding='utf8', names=['id','forme',"lemme","pos","pos_cattex09","igram1","igram2","igram3",'igram4','src'], quoting=csv.QUOTE_NONE, dtype=object) for f in files])

	### PRETRAITEMENT
		## si deux lignes consecutives commencent par 1 supprimer premier valeur (il s'agit d'un nombre limite de formes avec guillemets)
		df = df.loc[df.id.shift(-1) != df.id]

		
		## meme processus de traitement pour les caracteres que dans pretraitement_corpus.py
		'''
		enlever chiffres - necessaire pour tous
		guillemets avec point - necessaire pour tous
		eliminer lignes avec NaN (colonne formes ou lemme ou etiquette(ud/cattex)) - necessaire pour tous
		mots commencant par guillemet (eg : 'xirent) - necessaire pour lgerm
		'''
		df['forme'], df['lemme'] = df['forme'].str.replace('\d+', ''), df['lemme'].str.replace('\d+','')
		df['forme'], df['lemme'] = df['forme'].str.replace('.»', '"').replace('».','»'), df['lemme'].str.replace('.»','"').replace('».','»')
		df = df[~df.forme.isna()]
		df = df[~df.lemme.isna()]
		df = df[~df.pos.isna()]
		df = df[~df.pos_cattex09.isna()]
		df.loc[df['forme'].str.contains(r"^'[a-z]"), 'forme'] = 'forme'.replace("'","")

		fname = files[0].split('\\')[0]+'\\'+files[1].split('\\')[1]+'\\intermediaires\\'+str(files[1].split('\\')[1])+'_ca_udpipe.conllu'
		#df.to_csv(fname, sep='\t', encoding='utf8', header=None, index=False)

		with open(fname,'r',encoding='utf8') as f:
			corpus = f.read()
			len(corpus)

		## supp lignes vides
			corpus = corpus.replace('\n\n','\n').replace('.»', '"').replace('».','»').replace('""""""""""','"').replace('"""."','.').replace('""":"""',':').replace('""""','"').replace('"""','').replace('""','"').replace('..........................','.')
			List = corpus.split('\n')
		# ajout *FINPHRASE* entre fin de ligne et debut des metadonnees de la ligne suivante
			debut_ligne = [idx for idx, val in enumerate(List) if val.startswith('1\t')]
			for i, idx in enumerate(debut_ligne):
				List.insert(idx+i,"*FINPHRASE*\t*FINPHRASE*\t\t\t\t\t\t\t\t")
			corpus = '\n'.join(List)

			outname = fname.replace("udpipe.conllu",'udpipe_fin_phrases.conllu')
			with open(outname,'w',encoding='utf8') as f_sortie:
				f_sortie.write(corpus)


def metadata():
	for dir in glob.glob("*\\*\\intermediaires\\*_phrases.conllu"):
		col_names = ['id','form','lema','upos','cattex','inf1','inf2','inf3','inf4','src']
		df = pd.read_csv(dir, sep='\t', encoding='utf8', names=col_names ,quoting=csv.QUOTE_NONE)

		# PRETRAITEMENT CARACTERES
		# ## I. CHIFFRES ROMAINES : les chiffres romaines donnent les problemes a cause des points, recherce de ceulles qui contientn des points et des lettres et susbttution des points par >>
		df.loc[df.form.str.contains(r'\.(\w)'), 'form'] = df.form.str.replace('.','>>')

		## II. Points suspensifs
		df.loc[df.form.str.contains(r'\.\.\.'), 'form'] = df.form.str.replace(r'...','*pointsuspension*')
		#print(df.loc[df.form.str.contains(r'^\.[a-zA-Z]*\.')])

		## III. Guillemets """  et »
		df.loc[df.form.str.contains('"'), 'form'] = df.form.str.replace('"','*guillemets*')
		df.loc[df.form.str.contains('»'),'form'] = df.form.str.replace('»','*guillemets2*')

		# # FORMES VERS UNE LISTE
		formes = df.form.values.tolist()
		text = ' '.join(formes)
		text = text.replace('-','*barre*').replace('!,','! ,').replace('.,','. ,')
		
		## METADONNEES (sent id // text)
		lines = []
		nb = 0
		sent_id = []

		for line in text.split('*FINPHRASE* '):
			line = line.replace(r'^\n','')
			line = line.replace("  ","")
			if len(line)>1:
				nb+=1
				lines.append(f'# sent_id = {nb}\t# text = {line}')
				sent_id.append('# sent_id = '+ str(nb))


		## TABLEAU AVEC 2 COLONNES : SENT ID / PHRASE
		id_et_text = pd.DataFrame([x.split('\t') for x in lines], columns=['id','text'])
		

		# Ajout des sent_id + texte + espace dans les fichiers du corpus
		fname_avec_metadonnees = dir.replace('fin_phrases','fin_phrases_avec_metadonnees')

		with open(dir, 'r', encoding='utf8') as f:
			corpus = f.read()
			List = corpus.split('\n')
			
			## ajout espace entre fin de ligne et debut des metadonnees de la ligne suivante
			deb_ligne3 = [idx for idx, val in enumerate(List) if val.startswith('*FINPHRASE*')]

			for i, idx in enumerate(deb_ligne3):
				List.insert(idx+i,"\t\t\t\t\t\t\t\t\t\t")
			
			## ajout sent id
			debut_ligne = [idx for idx, val in enumerate(List) if val.startswith('1\t')]
			sent_nb = 0
			for i, idx in enumerate(debut_ligne):
				sent_nb+=1
				List.insert(idx+i,'##sent_id = '+ str(sent_nb)+"\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN")

			#ajout d'autre sent id qui sera remplace par la phrase corespondante a l'aide du tableau precedent (id_et_text)
			deb_ligne2 = [idx for idx, val in enumerate(List) if val.startswith('1\t')]
			sent_nb1 = 0
			for i, idx in enumerate(deb_ligne2):
				sent_nb1+=1
				List.insert(idx+i,'# sent_id = '+ str(sent_nb1)+"\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN")
			
			# ## vers tableau. 
			newdf = pd.DataFrame([x.split('\t') for x in List], columns=['id','form','lema','upos','cattex','inf1','inf2','inf3','inf4','src','?'])

			#newdf.to_csv('corpus_avec_id.csv', sep='\t', header=True,index=False)

			newdf['id'] = newdf['id'].replace(id_et_text.set_index('id')['text'])
			newdf['id'] = newdf['id'].str.replace('##','# ')
			#newdf['id'] = newdf['id'].str.replace(r'\.text$','.')
			del newdf['?']
			
			newdf.to_csv(fname_avec_metadonnees, encoding='utf-8', sep='\t',index=False,header=None)


# metadata()


def ud_metadata_final():
	'''
	Corpus d'apprentissage avec les metadonnes pret pour entrainement (suppresion caracteres/elements d'appui du prodessus de traitement precedent)
	'''
	for dir in glob.glob("*\\*\\intermediaires\\*_metadonnees.conllu"): # cambiar a *_avec_metadonnees.csv
		corpus_prep = open(dir,'r',encoding='utf8').read()
		corpus_prep = corpus_prep.replace('\tNaN','').replace('									','').replace('""""','"').replace('*guillemets*','"').replace('>>','.').replace('*pointsuspension*','...').replace('*barre*','-').replace('*guillemets2*','»').replace('\n*FINPHRASE*\t*FINPHRASE*\t\t\t\t\t\t\t\t','')

		fsortie_name = dir.replace("\\intermediaires","").replace("ca_udpipe_fin_phrases_avec_metadonnees.conllu","UDPIPE_ca_final.conllu")
		
		with open(fsortie_name,'w', encoding='utf8') as f:
			f.write(corpus_prep)


udpipe_mid_files() # dossier pour contenir fichiers intermetiaires
make_id_texte() # identification fin phrases
metadata() # ajout metadonnes (id+texte) fin phrases
ud_metadata_final()	# nettoyage et mise en forme finale
