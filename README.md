# Web Information Retrieval Project
Re-implementation of the paper "Identifying document topics using Wikipedia category network" by Peter Schonhofen (https://dl.acm.org/doi/10.1109/WI.2006.92) for WIR exam.

1) Run prepareWikipediaCorpus.py to transform Wikipedia dataset (URLs for download in /datasets) as a series of pickle dictionaries (in /corpus directory) that will be useful for the topic identification;
2) Run predict.py that will run the paper algorithm, contained in identifyDocumentTopic.py, on a set of 100 Wikipedia articles.
, saving results in /predictions.
