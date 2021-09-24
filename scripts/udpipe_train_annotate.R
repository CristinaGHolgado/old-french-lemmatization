library(udpipe)
train_annotate <- function(traindata, modelname, cc, outputname) {
     traindata <- traindata
     modelname <- modelname
     cc <- cc
     outputname <- outputname
         train <- udpipe_train(file = modelname, files_conllu_training = traindata, annotation_tokenizer = list(dimension = 24, epochs = 60, batch_size = 100, learning_rate=0.1, dropout = 0.5), annotation_tagger = list(iterations = 20, models = 1, provide_xpostag = 1, provide_lemma = 1, provide_feats = 1), annotation_parser = "none")
     load_model <- udpipe_load_model(file = modelname)
     corpuscontrole <- paste(readLines(cc))
     annotated <- udpipe_annotate(load_model, x = corpuscontrole, tokenizer = "vertical", tagger = "default", parser = "none", trace = FALSE)
     df <- as.data.frame(annotated)
     write.table(df[6:10], outputname, sep='\t', fileEncoding = "UTF-8", quote=FALSE,  col.names=FALSE, row.names=FALSE)
 }

