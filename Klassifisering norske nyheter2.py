# -*- coding: utf-8 -*-

import sys, os
import numpy as np
from sklearn.datasets import load_files
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn.grid_search import GridSearchCV

cat2name = {
	'KUL': 'Kultur og underholdning',
	'KRE': 'Kriminalitet og rettsvesen',
	'ULY': 'Ulykker og naturkatastrofer',
	'OKO': 'Økonomi og n\xc3\xa6ringsliv',
	'UTD': 'Utdanning',
	'NAT': 'Natur og miljø',
	'MED': 'Medisin og helse',
	'KUR': 'Kuriosa og kjendiser',
	'ARB': 'Arbeidsliv',
	'FRI': 'Fritid',
	'POL': 'Politikk',
	'REL': 'Religion og livssyn',
	'VIT': 'Vitenskap og teknologi',
	'SOS': 'Sosiale forhold',
	'SPO': 'Sport',
	'KRI': 'Krig og konflikter',
	'VAR': 'Vær',
	# disse tre er nye sammenslåinger av noen av kategoriene over
	'SAMF': 'Samfunnsspørsmål',
	'POLI': 'Politikk',
	'KULT': 'Kultur og underholdning'
}





# Plotting defaults
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
#%matplotlib inline
plt.rcParams['font.size'] = 18.0
plt.rcParams['figure.figsize'] = 26.0, 15.0



def plot_cm(cm, labels):
    # Compute percentanges
    percent = (cm*100.0)/np.array(np.matrix(cm.sum(axis=1)).T)  # Derp, I'm sure there's a better way
    print 'Confusion Matrix Stats'
    for i, label_i in enumerate(labels):
        for j, label_j in enumerate(labels):
            print "%s / %s: %.2f%% (%d/%d)" % (label_i, label_j, (percent[i][j]), cm[i][j], cm[i].sum())

    # Show confusion matrix
    # Thanks kermit666 from stackoverflow :)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    #ax.grid(b=False)
    cax = ax.matshow(percent, cmap='coolwarm',vmin=0,vmax=100)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    plt.title('Confusion matrix of the classifier')
    fig.colorbar(cax)
    ax.set_xticklabels([''] + labels)
    ax.set_yticklabels([''] + labels)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()


# <markdowncell>

# #Test rentekst

# <codecell>

# training_data = load_files('./ntb_data_6mars_rentekst/', encoding='utf-8', decode_error='ignore')
# docs_test = training_data.data

# text_clf = Pipeline([('vect', CountVectorizer()),
#                      ('tfidf', TfidfTransformer()),
#                      ('clf', MultinomialNB()),
# ])
# text_clf = text_clf.fit(training_data.data, training_data.target)

# predicted = text_clf.predict(docs_test)
# print "Rentekst-MultinomialNB mean: %s" % np.mean(predicted == training_data.target)

# text_clf = Pipeline([('vect', CountVectorizer()),
#                      ('tfidf', TfidfTransformer()),
#                      ('clf', SGDClassifier(loss='hinge', penalty='l2',
#                                            alpha=1e-3, n_iter=5)),
# ])
# _ = text_clf.fit(training_data.data, training_data.target)
# predicted = text_clf.predict(docs_test)

# print "Rentekst-SGDClassifier mean: %s" % np.mean(predicted == training_data.target)
#Rentekst-MultinomialNB mean: 0.722...
#Rentekst-SGDClassifier mean: 0.719...

# <codecell>

#bare den siste, nødvendigvis..
#print(metrics.classification_report(training_data.target, predicted, target_names=[cat2name[c] for c in training_data.target_names] ))
# comfusion matrix
# metrics.confusion_matrix(twenty_test.target, predicted)

# <markdowncell>

# # Test med tokenized stemmed (snowball) og stoppord-fjerning

# <codecell>

#training_data2 = load_files('./ntb_data_tokenized_stop_stemmed_13mars/', encoding='utf-8', decode_error='ignore')
# denne bør nok oppdateres når kjøringen min er ferdig
#docs_test = training_data2.data

# <codecell>

# text_clf = Pipeline([('vect', CountVectorizer()),
#                      ('tfidf', TfidfTransformer()),
#                      ('clf', MultinomialNB()),
# ])
# text_clf = text_clf.fit(training_data2.data, training_data2.target)

# predicted = text_clf.predict(docs_test)
# print "Stop-stem-MultinomialNB mean: %s" % np.mean(predicted == training_data2.target)

# text_clf = Pipeline([('vect', CountVectorizer()),
#                      ('tfidf', TfidfTransformer()),
#                      ('clf', SGDClassifier(loss='hinge', penalty='l2',
#                                            alpha=1e-3, n_iter=5)),
# ])
# _ = text_clf.fit(training_data2.data, training_data2.target)
# predicted = text_clf.predict(docs_test)

# print "Stop-stem-SGDClassifier mean: %s" % np.mean(predicted == training_data2.target)

# <codecell>

#print(metrics.classification_report(training_data.target, predicted, target_names=[cat2name[c] for c in training_data.target_names] ))

# <markdowncell>

# # Test med tokenized + stoppord, men ikke stemming (stemmeren er crappy)


training_data3 = load_files('./ntb_data_collapsed_4Helle/', encoding='utf-8', decode_error='ignore')


docs_test = training_data3.data


text_clf = Pipeline([('vect', CountVectorizer()),
                     ('tfidf', TfidfTransformer()),
                     ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                           alpha=1e-3, n_iter=5)),
])
_ = text_clf.fit(training_data3.data, training_data3.target)
predicted = text_clf.predict(docs_test)

print "Token-stop-SGDClassifier mean: %s" % np.mean(predicted == training_data3.target)

parameters = {'vect__ngram_range': [(1, 1), (1, 2)],
              'tfidf__use_idf': (True, False),
              'clf__alpha': (1e-2, 1e-3),
              }
# this is a gridsearch for text_clf, so a SGDClassifier
gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1) # use many cores if we has them
gs_clf = gs_clf.fit(training_data3.data[:30000], training_data3.target[:30000]) # dette kraska maskinen min...
best_parameters, score, _ = max(gs_clf.grid_scores_, key=lambda x: x[1])
for param_name in sorted(parameters.keys()):
    print("%s: %r" % (param_name, best_parameters[param_name]))

print "Best score: %s" % (score)


print "*"*20


# forsøker med Naive Bayse

text_clf = Pipeline([('vect', CountVectorizer()),
                     ('tfidf', TfidfTransformer()),
                     ('clf', MultinomialNB()),
])
text_clf = text_clf.fit(training_data3.data, training_data3.target)

predicted = text_clf.predict(docs_test)
print "Token-stop-MultinomialNB mean: %s" % np.mean(predicted == training_data3.target)




parameters = {'vect__ngram_range': [(1, 1), (1, 2)],
              'tfidf__use_idf': (True, False),
              'clf__alpha': (1e-2, 1e-3),
              }
# this is a gridsearch for text_clf, so a SGDClassifier
gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1) # use many cores if we has them
gs_clf = gs_clf.fit(training_data3.data[:30000], training_data3.target[:30000]) # dette kraska maskinen min...

best_parameters, score, _ = max(gs_clf.grid_scores_, key=lambda x: x[1])
for param_name in sorted(parameters.keys()):
    print("%s: %r" % (param_name, best_parameters[param_name]))
print "Best score: %s" % (score)

# med 2000 eksempler (dette endres med mer data)
#clf__alpha: 0.001
#tfidf__use_idf: True
#vect__ngram_range: (1, 1)
#0.6995 # økte til 72% med 5k eksempler


#
# Token-stop-SGDClassifier mean: 0.778942678164
# clf__alpha: 0.001
# tfidf__use_idf: True
# vect__ngram_range: (1, 2)
# Best score: 0.777766666667
# ********************
# Token-stop-MultinomialNB mean: 0.795953136057
# clf__alpha: 0.01
# tfidf__use_idf: False
# vect__ngram_range: (1, 1)
# Best score: 0.799733333333
#


# så plott noe..

from matplotlib.ticker import MultipleLocator

# def plot_cm(cm, labels):
#     # Compute percentanges
#     percent = (cm*100.0)/np.array(np.matrix(cm.sum(axis=1)).T)  # Derp, I'm sure there's a better way
#     print 'Confusion Matrix Stats'
#     for i, label_i in enumerate(labels):
#         for j, label_j in enumerate(labels):
#             print "%s / %s: %.2f%% (%d/%d)" % (label_i, label_j, (percent[i][j]), cm[i][j], cm[i].sum())
#
#     # Show confusion matrix
#     # Thanks kermit666 from stackoverflow :)
#     fig = plt.figure()
#     ax = fig.add_subplot(111)
#     #ax.grid(b=False)
#     cax = ax.matshow(percent, cmap='coolwarm',vmin=0,vmax=100)
#     ax.xaxis.set_major_locator(MultipleLocator(1))
#     ax.yaxis.set_major_locator(MultipleLocator(1))
#     plt.title('Confusion matrix of the classifier')
#     fig.colorbar(cax)
#     ax.set_xticklabels([''] + labels)
#     ax.set_yticklabels([''] + labels)
#     plt.xlabel('Predicted')
#     plt.ylabel('True')
#     plt.show()
#
#
# from sklearn import metrics
#
# print(metrics.classification_report(training_data.target, predicted,
#     target_names=[cat2name[c] for c in training_data.target_names]))
#
# cm = metrics.confusion_matrix(training_data.target, predicted)
# labels = [cat2name[c] for c in training_data.target_names] #training_data.target_names #
# plot_cm(cm, labels)
