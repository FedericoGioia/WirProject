import random
import os
import pickle
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

def reduce_ttl(input, factor, output):
    if not os.path.exists(output):
        with open(input, encoding="utf8") as i:
            input_list = i.readlines()
            reduced_length = int(len(input_list)*factor)
            reduced_input = random.sample(input_list, reduced_length)
            output_file = open(output, "w+")
            for line in reduced_input:
                output_file.write(line)
            output_file.close()

def stem_stop_remove(title):
    stop_words = set(stopwords.words("english"))
    title_tokens = word_tokenize(title)
    no_stopwords_title = [w for w in title_tokens if not w in stop_words]
    ps = PorterStemmer()
    result = ""
    for word in no_stopwords_title:
        result = result + ps.stem(word) + " "
    return result


if __name__ == "__main__":
    # paths of dataset files

    article_categories = "datasets/article_categories_en.ttl"
    article_categories_reduced = "datasets/article_categories_reduced.ttl"
    redirects = "datasets/redirects_en.ttl"
    redirects_reduced = "datasets/redirects_reduced.ttl"

    # reducing dataset to a feasible size

    reduce_ttl(article_categories, 0.1, article_categories_reduced)
    reduce_ttl(redirects, 0.3, redirects_reduced)



    # corpus steps

    article_prefix = "<http://dbpedia.org/resource/"
    categories_prefix = "<http://dbpedia.org/resource/Category:"

    article_to_categories = defaultdict(list)
    article_list = []
    with open(article_categories_reduced) as f:
        for line in f:
            splitted_line = line.split()
            article = splitted_line[0]
            category = splitted_line[2]
            article = article.replace(article_prefix, "").replace(">", "").replace("_", " ")
            article_list.append(article)
            category = category.replace(categories_prefix, "").replace(">", "").replace("_", " ")
            if category not in article_to_categories[article]:
                article_to_categories[article].append(category)
        dict_file = open("corpus/article_to_categories.pkl", "wb")
        pickle.dump(article_to_categories, dict_file)
        dict_file.close()


    stemmedarticle_to_articles = defaultdict(list)



    for article in article_list:
        stemmed_article = stem_stop_remove(article)
        if len(stemmed_article) > 1 and article not in stemmedarticle_to_articles[stemmed_article]:
            stemmedarticle_to_articles[stemmed_article].append(article)
    with open(redirects_reduced) as f:
        for line in f:
            splitted_line = line.split()
            redirect = splitted_line[0]
            article = splitted_line[2]
            redirect = redirect.replace(article_prefix, "").replace(">", "").replace("_", " ")
            article = article.replace(article_prefix, "").replace(">", "").replace("_", " ")
            stemmed_redirect = stem_stop_remove(redirect)
            if len(stemmed_redirect) > 1 and article in article_to_categories and article not in stemmedarticle_to_articles[stemmed_redirect]:
                stemmedarticle_to_articles[stemmed_redirect].append(article)
    dict_file = open("corpus/stemmedtitle_to_articles.pkl", "wb")
    pickle.dump(stemmedarticle_to_articles, dict_file)
    dict_file.close()

    stem_to_stemmedtitle = defaultdict(list)

    stems_vocabulary = stemmedarticle_to_articles.keys()
    for stemmed_title in stems_vocabulary:
        splitted_title = stemmed_title.split()
        for stemmed_word in splitted_title:
            if stemmed_title not in stem_to_stemmedtitle[stemmed_word]:
                stem_to_stemmedtitle[stemmed_word].append(stemmed_title)
    dict_file = open("corpus/stem_to_stemmedtitle.pkl", "wb")
    pickle.dump(stem_to_stemmedtitle, dict_file)
    dict_file.close()

    #dizionari di frequency e vocabulary di ogni category.
    dict_file_1 = open("corpus/stemmedtitle_to_articles.pkl", "rb")
    stemmedtitle_to_articles = pickle.load(dict_file_1)
    dict_file_1.close()

    dict_file_2 = open("corpus/article_to_categories.pkl", "rb")
    article_to_categories = pickle.load(dict_file_2)
    dict_file_2.close()

    stem_category_frequency = defaultdict(list)
    category_vocabulary = defaultdict(list)
    for stemmed_title, articles in stemmedtitle_to_articles.items():
    	for stem in stemmed_title.split():
    		for article in articles:
    			for category in article_to_categories[article]:
    				if stem not in category_vocabulary[category]:
    					category_vocabulary[category].append(stem)  #creo un dizionario con chiave category e valore le parole stemmate
    				if category not in stem_category_frequency[stem]:
    					stem_category_frequency[stem].append(category) #creo un dizionario con chiavi e valori invertiti a quello precedente
    stem_category_frequency = {k: len(v) for k, v in stem_category_frequency.items()} #modifico le values del dizionario delle frequencies mettendoci il numero delle categorie associate alla singola parola stemmata
    #salvataggio in files dei nuovi dizionari generati
    dict_file_3 = open("corpus/category_vocabulary.pkl", "wb")
    pickle.dump(category_vocabulary, dict_file_3)
    dict_file_3.close()

    dict_file_4 = open("corpus/stem_category_frequency.pkl", "wb")
    pickle.dump(stem_category_frequency, dict_file_4)
    dict_file_4.close()
