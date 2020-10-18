import pickle
import wikipedia
import numpy as np
import matplotlib.pyplot as plt
from identifyDocumentTopic import identify_topic
from os import path

def plot(title, x_lab, y_lab, x, y, x_tick=None, y_tick=None):
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(x_lab)
    plt.ylabel(y_lab)
    if x_tick is not None:
        plt.xticks(x_tick)
    if y_tick is not None:
        plt.yticks(y_tick)
    plt.savefig(path.join("predictions", title+".png"))
    plt.show()


if __name__ == "__main__":

    article_to_categories = pickle.load(open("corpus/article_to_categories.pkl", "rb"))
    stemmedtitle_to_articles = pickle.load(open("corpus/stemmedtitle_to_articles.pkl", "rb"))
    stem_to_stemmedtitle = pickle.load(open("corpus/stem_to_stemmedtitle.pkl", "rb"))
    category_vocabulary = pickle.load(open("corpus/category_vocabulary.pkl", "rb"))
    stem_category_frequency = pickle.load(open("corpus/stem_category_frequency.pkl", "rb"))
    categories = list(category_vocabulary.keys())


    articles = list(article_to_categories.keys())
    titles = np.random.choice(articles, 100)
    test_set = []

    for t in titles:
        try:
            page = wikipedia.page(title=t, pageid=None, auto_suggest=True, redirect=True, preload=False)
            doc_body = page.content
            test_set.append((t, doc_body))
        except:
            pass

    total_precision = []
    total_recall = []
    classification = []

    counter = 0
    for title, body in test_set:
        current_p = []
        current_r = []
        counter += 1
        print("Document no. " + str(counter))
        rank = identify_topic(body, categories, article_to_categories, stemmedtitle_to_articles, stem_to_stemmedtitle, category_vocabulary, stem_category_frequency, 1)
        ground_truth = article_to_categories[title]

        print(rank, ground_truth)
        print()

        for i in range(1, 11) :
            num = len([c for c in rank[:i] if c[0] in ground_truth])
            current_p.append(num/i)
            current_r.append(num/len(ground_truth))
        total_precision.append(current_p)
        total_recall.append(current_r)
        classification.append((title, ground_truth, rank))

    avg_prec = np.array(total_precision).mean(axis=0)
    avg_rec = np.array(total_recall).mean(axis=0)
    plot("precision-K", "K", "Precision", range(1, 11), avg_prec, x_tick=range(1, 11))
    plot("recall-K", "K", "Recall", range(1, 11), avg_rec, x_tick=range(1, 11))

    results_file = open("predictions/results-opt.txt", "w+")
    for title, true, pred in classification:
        results_file.write(title + "\t" + str(true) + "\t" + str(pred) + "\n" + "\n")
    results_file.close()
