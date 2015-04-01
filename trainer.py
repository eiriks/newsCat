#!/usr/bin/python2.7
# coding: utf-8
__author__ = 'eirikstavelin'

# Running through this: http://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html
# bruke denne som mal: http://stackoverflow.com/questions/19336497/using-sci-kit-learn-to-classify-text-with-a-large-corpus

import sys
import numpy as np
from sklearn.datasets import load_files
import time
start = time.time()

# det ser ut til at sciøaern ønsker seg numpy data matrise
#http://stackoverflow.com/questions/7061824/whats-the-most-efficient-way-to-convert-a-mysql-result-set-to-a-numpy-array
# plan: create giant list of document
# keep track of category somehow
# http://scikit-learn.org/dev/modules/feature_extraction.html#common-vectorizer-usage

training_data = load_files('./ntb_data/', encoding='utf-8', decode_error='ignore')  # ,encoding='utf-8' decode_error='ignore'

print "Training data loaded:" ,type(training_data), len(training_data) # <class 'sklearn.datasets.base.Bunch'> 5
print training_data.target_names

#print(training_data.target_names[training_data.target[0]])

print type(training_data.data[0]), len(training_data.data[0])

from sklearn.feature_extraction.text import CountVectorizer
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(training_data.data)

print count_vect.vocabulary_.get(u'krig')

from sklearn.feature_extraction.text import TfidfTransformer
tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
X_train_tf = tf_transformer.transform(X_train_counts)
print X_train_tf.shape

tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
print X_train_tfidf.shape

# training
from sklearn.naive_bayes import MultinomialNB

print "*"*20
print type(X_train_tfidf), X_train_tfidf.shape
print "*"*20
print type(training_data.target), len(training_data.target)
print "*"*20
clf = MultinomialNB().fit(X_train_tfidf, training_data.target) # scipy.sparse.csr.csr_matrix, numpy.ndarray # both of with 2257 units (matrix has 35788 cols as well)

#print twenty_train.target
docs_new = ['Jeg vinner neste valg på stortinget sier minister.', 'Målmann er vikti for å sikre seieren', "Renten må ned",
            "Storm ventes i Bergen", "Solskinn og nedbør.", "På scenen sang rytme publikum", "valgvaken var god stemning", "uvære storm nedbør",
            'God is love', 'OpenGL on the GPU is fast']

docs_new.append("Kasparov advarer Carlsen mot russiske konspirasjoner Tidenes beste sjakkspiller frykter sabotasje og "
                "spionasje mot Magnus Carlsen i Sotsji."
                " – Bullshit!, tordner sjakkforbundet - men Carlsen-leiren har tatt forholdsregler.")

docs_new.append("Det ble kamp om billettene til den kommende Tenacious D-konserten, da de ble lagt ut for salg i dag tidlig. "
                "Hele 1750 billetter ble revet vekk på bare 4 minutter. Dette er tall som Lars Tefre Baade, markedsanvarlig hos Rockefeller/John Dee/Sentrum Scene, synes er veldig imponerende, men ikke særlig overraskende. – Vi er helt utsolgt. Billettene var ute hos glade fans etter bare fire minutter. Det er stor stas å få Tenacious D til Norge! Allerede da vi slapp nyheten på tirsdag, skjønte vi at dette ville selge bra. Besøker mindre konsertlokaler")

docs_new.append("Vil trolig endre norsk rettspraksis Norge er ett av få land igjen i verden som ikke straffer en gjerningsmann som "
                "var psykotisk i gjerningsøyeblikket. Men nå skal Tilregnelighetsutvalget legge fram sitt reformforslag om norsk rettsvesen. "
                " AV  Marit Kolberg Journalist  Marit Kolberg Øystein Heggen - Foto: Anne Liv Ekroll / Anne Liv Ekroll, NRK Journalist  "
                "Øystein Heggen Anbefal Tweet +1 Send epost  Publisert i dag, for en time siden Rettssaken mot Anders Behring Breivik "
                "avdekket etter manges mening svakheter ved det norske rettssystemet. Rettspsykiaternes uenighet om hvorvidt han var "
                "strafferettslig tilregnelig eller ikke og den betydningen det ville få for straffeutmålingen, fikk mange til å ta til orde for en reform.")


docs_new.append("Svensk styringsrente på 0 prosent Historisk lav styringsrente hos våre naboer. Sentersjef på Svinesund jubler.  AV  Sebastian Nordli bylineNRK Journalist  Sebastian Nordli @nordli21 Byline Hilde ErlingsenNRK Journalist  Hilde Erlingsen Byline Siw Mariann Strømbeck - Foto: Photographer: Leif Ingvald Skaug /  Journalist  Siw Mariann Strømbeck Anbefal Tweet +1 Send epost  Publisert i dag, for 47 minutter siden  Oppdatert i dag, for 20 minutter siden Den svenske sentralbanken, Riksbanken, har senket styringsrenta med 0,25 prosentpoeng til 0 prosent.  – Inflasjonen er for lav. Riksbankens ledelse har derfor besluttet at pengepolitikken må bli mer ekspansiv, skriver Riksbanken i en pressemelding.  Rentenedsettelsen tirsdag var uventet stor. På forhånd var det ventet at nedgangen ville bli på mellom 0,05 og 0,10 prosent.  Negativ inflasjonstakt Forventningene om en rentenedgang har imidlertid vært økende de siste par ukene etter at konsumprisindeksen viste en uventet stor prisnedgang i september.  Inflasjonstakten i Sverige har vært negativ i sju av årets første ti måneder, og inflasjonen har vært angt unna målet på 2 prosent over tre år.  Riksbanken påpeker samtidig at når renta nå senkes til 0 prosent, øker faren for at privathusholdningenes gjeld stiger enda mer.")

X_new_counts = count_vect.transform(docs_new)

X_new_tfidf = tfidf_transformer.transform(X_new_counts)
#print "X_new_tfidf", X_new_tfidf
predicted = clf.predict(X_new_tfidf)
predict_proba = clf.predict_proba(X_new_tfidf)
#print "predicted", predicted

for doc, category, pro in zip(docs_new, predicted, predict_proba):
    print('%r => %s ' % (doc, training_data.target_names[category]))
    print('@ %s %s' % (max(pro), pro))

print "*"*60

# pipeline
from sklearn.pipeline import Pipeline
text_clf = Pipeline([('vect', CountVectorizer()),
                     ('tfidf', TfidfTransformer()),
                     ('clf', MultinomialNB()),
])
text_clf = text_clf.fit(training_data.data, training_data.target)

training_data = load_files('./ntb_data', encoding='utf-8', decode_error='ignore')

docs_test = training_data.data
predicted = text_clf.predict(docs_test)

print "MultinomialNB mean: %s" % np.mean(predicted == training_data.target)

print "*"*30


from sklearn.linear_model import SGDClassifier
text_clf = Pipeline([('vect', CountVectorizer()),
                     ('tfidf', TfidfTransformer()),
                     ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                           alpha=1e-3, n_iter=5)),
])
_ = text_clf.fit(training_data.data, training_data.target)
predicted = text_clf.predict(docs_test)

print "SGDClassifier mean: %s" % np.mean(predicted == training_data.target)
print "*"*30

from sklearn import metrics
print(metrics.classification_report(training_data.target, predicted,
    target_names=training_data.target_names))

print metrics.confusion_matrix(training_data.target, predicted)



print 'It took', time.time()-start, 'seconds.'

if __name__ == '__main__':
    print "Kjører fra terminal"

