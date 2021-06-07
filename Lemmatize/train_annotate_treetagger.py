import glob
import os
import time

def dirs_output():
    """
    Creation de sous-dossiers pour les fichiers intermediaires (necessaires uniquement pour le traitement) :
    """
    test_folders = []
    for dir in glob.glob("1-dossier_tests\\*\\"):
        test_folders.append(dir+'\\')
    for folder in test_folders:
        try:
            os.makedirs(folder+'CC_annotes')   
        except FileExistsError:
            pass

dirs_output()

def entrainement():
    for dir in glob.glob("1-dossier_tests\\*"):
        testname= dir.split('\\')[1]
        lexiques_tests = glob.glob(os.path.join(dir,"*lexique.csv"))
        corpus_apprentissage = glob.glob(os.path.join(dir,"*(treetagger)_final.csv"))
        path = [item.split("\\")[0] for item in lexiques_tests]
        path_par_f = [f+"\\"+testname+"\\test.par" for f in path]
        for f in lexiques_tests:
            for c in corpus_apprentissage:
                for p in path_par_f:
                    run_train = f"train-tree-tagger -st PONfrt {f} cattex2009_open_class.txt {c} {p}"
                os.popen(run_train)

# lib timer ajouté car sinon le script s'arrête après la dernière fonction.
time.sleep(10)
entrainement()


time.sleep(10)
# IV. ## ETIQUETTER CORPUS D'APPRENTISSAGE
#fichier de sortie : corpus_controle_tagged.csv

def tag_corpus_contr():
    for dir in glob.glob("1-dossier_tests\\*"):
        fichiers_cc = glob.glob(os.path.join(dir,"*_controle_final.csv"))
        testname= dir.split('\\')[1]
        path = [item.split("\\")[0] for item in fichiers_cc]
        sortie_controle = [f+"\\"+testname+"\\CC_annotes\\TREETAGGER_corpus_controle_tagged.csv" for f in path]
        par_files = glob.glob(os.path.join(dir,"*.par"))
        unknown_f = [f+"\\"+testname+"\\CC_annotes\\TREETAGGER(unknown)_corpus_controle_tagged.csv" for f in path]
        for f in fichiers_cc:
            for p in sortie_controle:
                for par in par_files:
                    tt_tag = f"tree-tagger {par} -token -lemma -no-unknown {f} >> {p}"
                    for u in unknown_f:
                        tt_tag_avec_unknown = f"tree-tagger {par} -token -lemma {f} >> {u}"
                    os.popen(tt_tag_avec_unknown)
                os.popen(tt_tag)

time.sleep(5)
tag_corpus_contr()
