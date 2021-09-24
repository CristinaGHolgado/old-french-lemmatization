import pandas as pd
import csv
import glob
import os
import re
import shutil
import subprocess
import io

pie_path = r"C:\\Python36\\Lib\\site-packages\\pie"


def dirs_output():
	"""
	Make subfolders for preprocessing and annotated files

	"""
	test_folders = []
	for dir in glob.glob("1-dossier_tests\\*\\"):
		test_folders.append(dir+'\\')
	for folder in test_folders:
		try:
			os.makedirs(folder+'intermediaires')
			os.makedirs(folder+'CC_annotes')
			print("Directory '%s' created" %directory) 
		except FileExistsError:
			pass


print("Corpus d'apprentissage\n-----------------------")

def corpus_app(treetagger=None, nlppie=None):
	"""
	Prepares TreeTagger / NLP-PIE traning corpus 	
	"""
	for dir in glob.glob("*\\*\\CORPUS_APPRENTISSAGE"):
		files = glob.glob(os.path.join(dir,"*.conllu"))

	### LECTURE
		df_CA = pd.concat([pd.read_csv(f, sep='\t', encoding='utf8', names=['id','forme',"lemme","pos","pos_cattex09","igram1","igram2","igram3",'igram4','src'], quoting=csv.QUOTE_NONE, dtype=object) for f in files])
		num_test = dir.split('\\')[1]
		ca_path = dir.split('\\')[0]+"\\"+dir.split('\\')[1]+"\\"+num_test	# test names & path

		print(f"Test {num_test} : {len(df_CA)} lignes.") # test name, number of initial lines

	### GENERAL PREPROCESSING
		'''
		remove numbers, line with empty values, process quoting
		'''
		df_CA['forme'], df_CA['lemme'] = df_CA['forme'].str.replace('\d+', ''), df_CA['lemme'].str.replace('\d+','')
		df_CA['forme'], df_CA['lemme'] = df_CA['forme'].str.replace('.»', '"').replace('».','»'), df_CA['lemme'].str.replace('.»','"').replace('».','»')
		df_CA.loc[df_CA['forme'].str.contains(r"^'[a-z]", na=False), 'forme'] = 'forme'.replace("'","")
		df_CA['forme'] = df_CA['forme'].str.replace(' ', '_')
		
		df_raw = df_CA	# copie du df avant pretraitement pour calculs
		df_CA = df_CA[~df_CA.forme.isna()]
		df_CA = df_CA[~df_CA.lemme.isna()]
		df_CA = df_CA[~df_CA.pos_cattex09.isna()]
		df_CA = df_CA[~df_CA.lemme.str.contains('no_lem')]


	### save & info skkiped lines, skipped lines to csv
		print('\t', len(df_CA), " lignes après traitement.", len(df_raw)-len(df_CA),' ignorées.\n')
		skip_l = df_raw.loc[~df_raw.set_index(list(df_raw.columns)).index.isin(df_CA.set_index(list(df_CA.columns)).index)]
		fname_supprimes = "formes_supprimes\\"+ str(num_test)+"_formes_supprimes.csv"
		skip_l.to_csv(fname_supprimes, encoding='utf-8', sep='\t', header=False, index=None)
		print('Lignes ignorées sauvegardés dans /formes_supprimes')
		print('- Aperçu\n--------------')
		print(skip_l[['id','forme','pos','pos_cattex09','lemme']])

		
	### PRETRAITEMENT SPECIFIQUE, PREPARATION DU CORPUS FINAL D'APPRENTISSAGE POUR TOUS LES OUTILS
		def make_ca_final():
			"""
			- corpus apprentissage = forme/pos_cattex/lemme
			- TreeTagger = forme + pos_cattex
			"""

		## CA TOUS
			ca_df = df_CA[['forme','pos_cattex09','lemme']]
			path_save_ca = dir.split('\\')[0]+"\\"+dir.split('\\')[1]+"\\intermediaires\\"+num_test+'_corpus_d_apprentissage.csv'
			print(path_save_ca)
			ca_df.to_csv(path_save_ca, encoding='utf-8', sep='\t', header=False, index=None)

			with open(path_save_ca,'r',encoding='utf-8') as f:
				ca = f.read()
				# il faut suivre cet ordre de remplacement
				ca = ca.replace('""""""""""','"').replace('"""."','.').replace('""":"""',':').replace('""""','"').replace('"""','').replace('""','"').replace('..........................','.')
				path_save_ca = path_save_ca.replace('.csv','_final.csv').replace("intermediaires\\","")
				with open(path_save_ca,'w', encoding='utf-8') as f_out:
					f_out.write(ca)


##
		def traindata_treetagger():
			ca_treetagger = df_CA[['forme','pos_cattex09']]
			save_ca_tree = dir.split('\\')[0]+"\\"+dir.split('\\')[1]+"\\intermediaires\\"+num_test+'(treetagger).csv'
			ca_treetagger.to_csv(save_ca_tree, encoding='utf-8', sep='\t', header=False, index=None)

			with open(save_ca_tree,'r',encoding='utf-8') as f:
				ca_tree = f.read()
				# il faut suivre cet ordre de remplacement
				ca_tree = ca_tree.replace('""""""""""','"').replace('"""."','.').replace('""":"""',':').replace('""""','"').replace('"""','').replace('""','"').replace('..........................','.')
				path_save_ca_tree = save_ca_tree.replace('.csv','_final.csv').replace("intermediaires\\","")
				with open(path_save_ca_tree,'w', encoding='utf-8') as f_out:
					f_out.write(ca_tree)


		
		def traindata_nlppie():
			"""
			Prepares NLP-PIE training data.

			Returns
			-------
			file object1 : 
				training_lemma.csv (forms + lemmas)
			file object2 :
				training_pos.csv (forms + tags)

			"""
			pie_lemmes = df_CA[['forme','lemme']]
			pie_lemmes.rename(columns = {'forme':'token','lemme':'lemma'}, inplace = True)

			pie_tags = df_CA[['forme','pos_cattex09']]
			pie_tags.rename(columns = {'forme':'token','pos_cattex09':'pos'}, inplace = True)
			path_save_pie_lemmes = dir.split('\\')[0]+"\\"+dir.split('\\')[1]+"\\intermediaires\\"+num_test+'_PIE(lemmes)_ca.csv'
			path_save_pie_tags = dir.split('\\')[0]+"\\"+dir.split('\\')[1]+"\\intermediaires\\"+num_test+'_PIE(tags)_ca.csv'
			pie_lemmes.to_csv(path_save_pie_lemmes, encoding='utf-8', sep='\t', index=None)
			pie_tags.to_csv(path_save_pie_tags, encoding='utf-8', sep='\t', index=None)

			# """""""""" vers "
			with open(path_save_pie_lemmes,'r',encoding='utf-8') as f1, open(path_save_pie_tags, 'r',encoding='utf-8') as f2:
				lemmes = f1.read()
				tags = f2.read()
				# il faut suivre cet ordre de remplacement
				lemmes = lemmes.replace('""""""""""','"').replace('"""."','.').replace('""":"""',':').replace('""""','"').replace('"""','').replace('""','"').replace('..........................','.')
				tags = tags.replace('""""""""""','"').replace('"""."','.').replace('""":"""',':').replace('""""','"').replace('"""','').replace('""','"').replace('..........................','.')
				
				final_form_lem = path_save_pie_lemmes.replace('.csv','_final.csv').replace("intermediaires\\","")
				final_form_tags = path_save_pie_tags.replace('.csv','_final.csv').replace("intermediaires\\","")

				with io.open(final_form_lem,'w', encoding='utf-8') as f_out_lem:
					f_out_lem.write(lemmes)
				with io.open(final_form_tags, 'w', encoding='utf-8') as f_out_tag:
					f_out_tag.write(tags)

		make_ca_final()
		traindata_treetagger()
		traindata_nlppie()
corpus_app()
