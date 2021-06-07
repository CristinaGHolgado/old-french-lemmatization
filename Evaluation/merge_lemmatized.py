import os
import glob
import pandas as pd

def merge_lemmatized_tests():
	"""	Merge lemmatized files into a main df for each test
	"""
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

