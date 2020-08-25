import glob
import os
import subprocess





def lancer_lgerm_cc():
	for dir in glob.glob("1-dossier_tests\\*\\*iso*"):
		print(dir)
		# bash_str = "bash lgerm.bash -init medieval_cattex.ini "+ '"'+dir+'"'
		# run_lgerm = ["bash", "-c", bash_str]
		# subprocess.call(run_lgerm)

# lancer_lgerm_cc()

## puis merge manualmente los 2 ficheros del test 1 y lanzar :

def cc_annote_vers_utf8():
	for dir in glob.glob("tmp\\*iso_5*"):
		commande = "iconv -f iso-8859-1 -t utf-8 "+"'"+dir+"'"+" > "+"'1-dossier_tests\\TEST_"+dir.replace("tmp\\",'').split('_')[1]+"\\CC_annotes\\cc_lgerm(utf8)_tagged.txt"+"'; exit"
		conv = ["bash", "-c", commande]
		subprocess.call(conv)

	# # concatener fichiers test1
	# commande = 'copy '+ '1-corpus_src(normalise)_tests\\*pt*utf8*.txt'+ ' 1-corpus_src(normalise)_tests\\TEST_1_corpus_controle_final(lgerm)_iso_5_utf8.txt'
	# os.system(commande)

cc_annote_vers_utf8()