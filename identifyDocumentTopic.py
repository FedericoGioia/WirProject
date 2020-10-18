from prepareWikipediaCorpus import stem_stop_remove
from collections import defaultdict
from math import log

def word_support(w, t, doc_words):
    stemmed_title_words = t.split()
    if w in stemmed_title_words:
        stemmed_title_words.remove(w)
        count = 0
        for word in stemmed_title_words:
            if word not in doc_words:
                count += 1
                if count == 2:
                    return False
        return True
    else:
        return False

def identify_topic(doc_body, categories, article_to_categories, stemmedtitle_to_articles, stem_to_stemmedtitle, category_vocabulary, stem_category_frequency, opt):

    # remove stopwords and perform stemming, remove words not occurring in Wikipedia article titles
    stemmed_doc_body = []
    revised_body = stem_stop_remove(doc_body).split()
    for word in revised_body:
        if word in stem_to_stemmedtitle:
            stemmed_doc_body.append(word)

    word_frequencies = defaultdict(int)
    for word in stemmed_doc_body:
        if not word in word_frequencies.keys():
            word_frequencies[word] = stemmed_doc_body.count(word)


    # collect words of the document and weight them by Rw = TFw * log(N/CFw)
    # where TFw is term frequency, N is the number of categories and CFw is the
    # number of categories containing "w" in their vocabulary

    weighted_words = defaultdict(float)
    for word in stemmed_doc_body:
        TFw = word_frequencies[word]
        N = len(categories)
        CFw = stem_category_frequency[word]

        Rw = TFw * log(N / CFw)

        weighted_words[word] = Rw

    print("primo fattore")
    # collect Wikipedia titles whose words (with the possible exception of one)
    # are all present in the document, and weight them by Rt = sum w->t (Rw * 1/Tw * 1/At * St/Lt)
    # where Tw denotes Wikipedia titles with "w" inside, At is the number of articles pointed by
    # title "t", Lt stands for the title length (in words) and St is the number of title words
    # present in the document

    weighted_titles = defaultdict(float)
    support_category_words = defaultdict(list)
    for t, articles in stemmedtitle_to_articles.items():
        Rt = 0
        At = len(articles)
        Lt = len(t.split())
        St = 0
        for word in t.split():
            if word in weighted_words:
                St =+ 1
        for w, Rw in weighted_words.items():
            if word_support(w, t, weighted_words.keys()):
                for article in articles:
                    for c in article_to_categories[article]:
                        if w not in support_category_words[c]:
                            support_category_words[c].append(w)
                Tw = len(stem_to_stemmedtitle[w])
                Rt += Rw * (1/Tw) * (1/At) * (St/Lt)
        if Rt != 0:
            for article in articles:
                if article not in weighted_titles or weighted_titles[article] < Rt:
                    weighted_titles[article] = Rt
    # in the above if, we take the maximum Rt (Ra) of an article pointed by different stemmed titles

    print("secondo fattore")


    categories_to_articles = defaultdict(list)
    articles = weighted_titles.keys()
    for a in articles:
        categories_list = article_to_categories[a]
        for c in categories_list:
            if not a in categories_to_articles[c]:
                categories_to_articles[c].append(a)

    print("terzo fattore")

    # collect Wikipedia categories assigned to the articles and weight them by Rc = sum a->c Ra

    weighted_categories = defaultdict(float)

    if (opt):
        for category, words in category_vocabulary.items():
            vc = len(support_category_words[category])
            dc = len(words)
            category_weight = 0
            for a in categories_to_articles[category]:
                category_weight += weighted_titles[a]
            weighted_categories[category] = (vc/dc) * category_weight

        #optimization with decay_value
        decay_value = {}
        for k in word_frequencies.keys():
            decay_value[k] = 1
        sorted_weighted_categories = sorted(weighted_categories.items(), key = lambda x: x[1], reverse = True)
        for category, weight in sorted_weighted_categories:
            num = sum([decay_value[stem] for stem in support_category_words[category]])
            den = len(support_category_words[category])
            if den != 0:
                weighted_categories[category] = weight*(num/den)
            for stemmed_word in support_category_words[category]:
                decay_value[stemmed_word] /= 2

    else:
        for category, articles in categories_to_articles.items():
            category_weight = 0
            for a in articles:
                category_weight += weighted_titles[a]
            weighted_categories[category] = category_weight

    print("quarto fattore")

    sorted_weighted_categories = sorted(weighted_categories.items(), key = lambda x: x[1], reverse = True)

    return sorted_weighted_categories[:10]
