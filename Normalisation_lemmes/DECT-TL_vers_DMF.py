import pandas as pd
import csv
import glob
import os
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def transformation(dect_dmf, tl_dmf, path_corpus):
  """Conversion of DECT|TL lemmas into DMF lemmas
  
  Parameters
  ----------
  dect_dmf : str
    path to dect-dmf file
  tl_dmf : str
    path to dect-dmf file
  path_corpus : str
    path to corpus folder containing conllu files. Files to be normalized.

  Returns
  -------
    file object
  """

  print("Normalisation DECT en DMF ...\n")
  ###################
  # TABLEAUX LEMMES #
  ###################
  dmf_df = pd.read_csv(dect_dmf, 
                    sep='\t',
                    encoding='utf-8', index_col=False,
                    names=['DECT', 'lemma'],
                    dtype=object,
                    quoting=csv.QUOTE_NONE)
  tl_df = pd.read_csv(tl_dmf, 
                    sep='\t',
                    encoding='utf-8',
                    dtype=object,
                    quoting=csv.QUOTE_NONE)
 
  dmf_df = dmf_df.dropna()
  tl_df = tl_df.dropna()

  tl_df.loc[tl_df['msd_cattex_conv'].eq('NOMpro') , 'TL'] = tl_df['TL'].str.capitalize()  ## Mise en majuscule les NOMpro dans le tableau TL-DMF (ils sont en minuscule dans les tableaux de correspondance de lemmes)
  tl_df.loc[tl_df['msd_cattex_conv'].eq('NOMpro') , 'DMF'] = tl_df['DMF'].str.capitalize()
  tl_df.TL = tl_df.TL.str.replace(r' \([a-zA-Z]{0}','__')
  tl_df.TL = tl_df.TL.str.replace(r'[a-z]{0}\)','')
  tl_df.TL = tl_df.TL.str.replace('/','__')
  tl_df['TL'] = tl_df['TL'].str.replace(r'\d+','')  # Suppression chiffres tableau TL-DMF (on a les etiquettes)
  
  tl_df['lemmes_commun'] = tl_df.apply(lambda x: str(x.DMF) in list(str(x.TL).split('__')), axis=1).astype(str) # Lorqu'il y a plusieurs lemmes dans la colonne TL, si un des lemmes TL apparait dans le corpus, laisser le seul lemme qui apparait et supprimer les autres.
  tl_df.loc[tl_df['lemmes_commun'].astype(str).str.contains('True'), 'TL'] = tl_df['DMF']

  tl_df['etiq_lem'] = '__'+tl_df[['msd_cattex_conv','TL']].agg('__'.join, axis=1)+'__' # Concatenation de la colonne etiquettes msd-cattex et la colonne des lemmes TL (e.g.: NOMcom abeie) dans une colonne unique.


  ##########
  # CORPUS #
  ##########
  files = glob.glob(os.path.join(path_corpus,"*.conllu")) # lecture fichiers du corpus a normaliser.
  for f in files:
    print(f.split('//')[-1].replace('corpus_a_normaliser\\',''))
    corpus = pd.read_csv(f,
                     sep='\t',
                     encoding='utf-8',
                     names=['id','forme', "lemme", "pos", "pos+", "imorph1", "imorph2","imorph3",'imorph4','src'],
                     quoting=csv.QUOTE_NONE,
                     dtype='object')

    corpus["ancien_lem"] = corpus['lemme']  # copie de la colonne lemmes



  #################
  # NORMALISATION #
  #################

  # 1. DECT > DMF
    corpus['lemme'] = corpus['lemme'].replace(dmf_df.set_index('DECT')['lemma']+'>')   # Si lemme DECT du corpus dans lemme DECT du tableau DECT-DMF, remplacer par lemme DMF correspondant. Ajout d'identificateur '>'

    print("==========================") ## Calcul du nombre de lemmes remplaces.
    print('Taille corpus :', len(corpus), 'formes')
    print('dont', len(corpus[corpus.lemme.str.contains('>')]), 'lemmes DECT remplaces en DMF.')
    print('soit le ', round(len(corpus[corpus.lemme.str.contains('>')])*100/len(corpus),3), '%')
    print('Restent : ', len(corpus)-len(corpus[corpus.lemme.str.contains('>')]),'lemmes DECT')
    print('\n--\n')
  
  # 2. TL > DMF

    corpus["lemme"] = corpus['lemme'].str.replace(r'\d+','')  # Suppresion chiffres chans la colonne lemmes pour conversion TL-DMF

    corpus['etiq_lem_corp'] = corpus['pos+'].str.replace(r'ABR.*[a-z]$','OUT').str.replace(r'ADJ.*[a-z]$','APD').str.replace(r'ADVneg','APD').str.replace(r'ADV.*[a-z]$','ADV').str.replace(r'CON.*[a-z]$','CON').str.replace('DETdef','DET').str.replace('DETndf','DET').str.replace(r'DET.*[a-z]$','APD').str.replace(r'ETR.*[a-z]$','ETR').str.replace(r'INJ.*[a-z]$','INJ').str.replace(r'PONfrt','-P-O-Nfrt').str.replace(r'PON.*[a-z]$','PON').str.replace(r'-P-O-Nfrt','PONfrt').str.replace(r'PRE.*','PRE').str.replace(r'PROper','P-R-O').str.replace(r'PRO.*[a-z]$','APD').str.replace(r'P-R-O','PRO').str.replace(r'RED','OUT').str.replace(r'RES','OUT').str.replace(r'VER.*[a-z]$','VER').str.replace(r'REL.*[a-z]$','OUT').str.replace(r'^((?!ABR|ADV|APD|OUT|ADV|CON|DETdef|DETndf|DET|ETR|INJ|PONfrt|PON|PRE|PROper|PRO|NOMcom|NOMpro|RES|VER|REL)).*$','OUT') # nouvelle colonne avec normalisation etiquettes  
    corpus['etiq_lem_corp'] = '__'+corpus[['etiq_lem_corp','lemme']].agg('__'.join, axis=1)+'__' # concatenation des lemmes et des etiquettes normalises (etiquette+lemme)
    corpus['etiq_lem_corp'] = corpus['etiq_lem_corp'].replace(r'^"','')
    corpus['etiq_lem_corp'] = corpus['etiq_lem_corp'].replace(tl_df.set_index('etiq_lem')['DMF']+'<') # Si etiquette et lemme corpus dans etiquette et lemme tableau TL-DMF, remplacer par lemme DMF du tableau.

    nom_fich = "intermediaires\\dect_en_dmf_"+os.path.basename(f)
    corpus.to_csv(nom_fich, sep='\t', encoding='utf-8', index=False, header=False)



  def transformation2(dectdmfpath_corpus):
    print("Normalisation TL en DMF ...\n")

    files = glob.glob(os.path.join(dectdmfpath_corpus,"*.conllu"))
    for f in files:
      print(f.split('//')[-1].replace('intermediaires\\',''))
      corpus2 = pd.read_csv(f,
                       sep='\t',
                       encoding='utf-8',
                       names=['id','forme', "lemme", "pos", "pos+", "imorph1", "imorph2","imorph3",'imorph4','src','ancien_lem','etiq_lem_corp'],
                       quoting=csv.QUOTE_NONE,
                       dtype='object')

      print(corpus2)
      corpus2.loc[corpus2['etiq_lem_corp'].str.contains('<'), 'lemme'] = corpus2['etiq_lem_corp']
      print("==========================")
      print(len(corpus2[corpus2.lemme.str.contains('<')]), 'lemmes TL(DECT) remplaces en DMF.')

      dect_restants = corpus2[~corpus2.lemme.str.contains('>|<')]
      nom_dect_restants = "dect_restants\\dect_restants(tout)"+os.path.basename(f)
      dect_restants.to_csv(nom_dect_restants, encoding='utf8', sep='\t')
      dect_sans_ponct = dect_restants[~dect_restants["pos+"].str.contains('PON')]
      nom_dect_restants_no_ponct = "dect_restants\\dect_restants(no_ponct)"+os.path.basename(f)
      dect_sans_ponct.to_csv(nom_dect_restants_no_ponct, encoding='utf-8', sep='\t')

      print('soit le ', round(len(corpus2[corpus2.lemme.str.contains('<|>')])*100/len(corpus2), 3), '% restant du corpus.')
      print('Restent : ', len(corpus2)-len(corpus2[corpus2.lemme.str.contains('<|>')]),'lemmes DECT')
      print('\n\n---\n\n')

  # # #### Modification de la source

      # modifier la source DECT a DMF/TL dans la colonne src
      cols = corpus2.columns[corpus2.columns.str.contains('src')]
      corpus2[cols] = corpus2[cols].mask(corpus2[cols].apply(lambda x: corpus2.lemme.str.contains(">|<")), corpus2['src'].str[:-4] + "DMF", axis=0)
      corpus2['src'] = corpus2['src'] + "|LemmaDECT=" + corpus2.ancien_lem


      corpus2['src'] = corpus2.src.str.replace(r'\|.*LemmaSrc=DECT\|LemmaDECT=.*','|LemmaSrc=DECT')
      corpus2['lemme'] = corpus2['lemme'].str.replace('>|<', '')
      del corpus2['ancien_lem']
      del corpus2['etiq_lem_corp']

      nom_fich = "corpus_normalise\\normalise(lemmes_corriges)_"+os.path.basename(f)
      corpus2.to_csv(nom_fich, sep='\t', encoding='utf-8', index=False, header=False)
      print('Fichiers normalises dans : ', nom_fich)

  transformation2('intermediaires')




transformation('correspondances_lemmes\\dect_en_dmf.csv','correspondances_lemmes\\convDECT2DMF.tsv', 'corpus_a_normaliser\\BFMGOLDLEM')
