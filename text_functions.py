#!/usr/bin/python
# encoding: utf-8
#
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import nltk
from norske_stammer import stem_list

# dette er settet av NLTKs og toppen av liste til Gyri & gutta på Aksis
stoppord = ['vart', 'over', 'ogs\xc3\xa5', 'skal', 'hele', 'andre', 'gang', 'vere', 'dere', 'henne', 'alle', 'han', 'begge', 's\xc3\xa5', 'sier', 'd\xc3\xa5', 'to', 'ved', 'f\xc3\xa5', 'under', 'hvor', 'har', 'korso', 'oss', 'ditt', 'dag', 'opp', 'di', 'n\xc3\xa5r', 'de', 'da', 'f\xc3\xa5r', 'noko', 'du', 'din', 'ikkje', 'hossen', 'mykje', 'tre', 'denne', 'ut', 'deim', 'f\xc3\xb8rste', 'upp', 'ville', 'blitt', 'en', 'hvem', 'kunne', 'mi', 'skulle', 'nokon', 'kvifor', 'seg', 'bare', 'et', 'hver', 'blei', 'somt', 'inni', 'er', 'hvorfor', 'g\xc3\xa5r', 'ingi', 'for', 'ned', 'kun', 'bli', 'siste', 'ble', 'b\xc3\xa5e', 'med', 'meg', 'mitt', 'men', 'flere', 'b\xc3\xa5de', 'fordi', 'hoss', 'mer', 'nokre', 'hadde', 'sidan', 'ja', 'om', 'v\xc3\xa5r', 's\xc3\xa5nn', 'ett', 'og', 'm\xc3\xa5', 'kommer', '\xc3\xa5r', 'ein', 'hennar', 'meget', 'samme', 'hva', 'hennes', 'som', 'korleis', 'vil', 'dykkar', 'hvordan', 'fra', 'sine', 'kom', 'her', 'kven', 'ingen', '\xc3\xa5', 'varte', 'ikke', 'deira', 'noen', 'jeg', 'f\xc3\xb8r', 'var', 'sitt', 'p\xc3\xa5', 'eg', 'store', 'mellom', 'fikk', 'uten', 'hun', 'sj\xc3\xb8l', 'honom', 'mine', 'hvilken', 'ho', 'ha', 'kvar', 'me', 'inkje', 'verte', 'eit', 'deires', 'etter', 'der', 'det', 'um', 'dei', 'dykk', 'dem', 'den', 'deg', 'mener', 'v\xc3\xa6rt', 'vors', 'vi', 'av', 'slik', 'vort', 'inn', 'blir', 'at', 'v\xc3\xa6re', 'mye', 'vore', 'hoe', 'min', 'elles', 'eller', 'deres', 'enn', 'hvilke', 'til', 'sia', 'disse', 'noe', 'nokor', 'selv', 'sin', 'hvis', 'nye', 'siden', 'eitt', 'kva', 'dette', 'kan', 'kvi', 'hans', 'kvarhelst', 'mot', 'medan', 'man', 'somme', 'i', 'no', 'si', 'so', 'noka', 'mange', 'sa', 'n\xc3\xa5', 'hj\xc3\xa5']
stoppord = ['vart', 'over', 'også', 'skal', 'hele', 'andre', 'gang', 'vere', 'dere', 'henne', 'alle', 'han', 'begge', 'så', 'sier', 'då', 'to', 'ved', 'få', 'under', 'hvor', 'har', 'korso', 'oss', 'ditt', 'dag', 'opp', 'di', 'når', 'de', 'da', 'får', 'noko', 'du', 'din', 'ikkje', 'hossen', 'mykje', 'tre', 'denne', 'ut', 'deim', 'første', 'upp', 'ville', 'blitt', 'en', 'hvem', 'kunne', 'mi', 'skulle', 'nokon', 'seg', 'bare', 'et', 'hver', 'blei', 'somt', 'inni', 'er', 'hvorfor', 'går', 'ingi', 'for', 'ned', 'kun', 'bli', 'siste', 'ble', 'båe', 'med', 'meg', 'mitt', 'men', 'flere', 'både', 'fordi', 'hoss', 'mer', 'nokre', 'hadde', 'sidan', 'ja', 'om', 'vår', 'sånn', 'ett', 'og', 'må', 'kommer', 'år', 'ein', 'hennar', 'meget', 'samme', 'hva', 'hennes', 'som', 'korleis', 'vil', 'dykkar', 'hvordan', 'fra', 'sine', 'kom', 'her', 'kven', 'ingen', 'å', 'varte', 'ikke', 'deira', 'noen', 'jeg', 'før', 'var', 'sitt', 'på', 'eg', 'store', 'mellom', 'fikk', 'uten', 'hun', 'sjøl', 'honom', 'mine', 'hvilken', 'ho', 'ha', 'kvar', 'me', 'inkje', 'verte', 'eit', 'deires', 'etter', 'der', 'det', 'um', 'dei', 'dykk', 'dem', 'den', 'deg', 'mener', 'vært', 'vors', 'vi', 'av', 'slik', 'vort', 'inn', 'blir', 'at', 'være', 'mye', 'vore', 'hoe', 'min', 'elles', 'eller', 'deres', 'enn', 'hvilke', 'til', 'sia', 'disse', 'noe', 'nokor', 'selv', 'sin', 'hvis', 'nye', 'siden', 'eitt', 'kva', 'dette', 'kan', 'kvi', 'hans', 'kvarhelst', 'mot', 'man', 'i', 'no', 'si', 'so', 'noka', 'mange', 'sa', 'nå']


def remove_stopwords(words):
    return [w for w in words if not w in stoppord]

def tokenize_remove_stopwords(text):
    words = nltk.wordpunct_tokenize(text)# text.decode('utf8')
    words = remove_stopwords(words)
    return " ".join(words)

def tokenize_remove_stopwords_stem(text):
    '''Uses the home-made norwegian stemmer based on a dict with words from Gullkorpuset
    This is by no means perfect, but it works on the few words that are in the dict'''
    words = nltk.wordpunct_tokenize(text)# text.decode('utf8')
    # remove stopwords
    words = remove_stopwords(words)
    # and do some stemming
    words = stem_list(words)
    return " ".join(words)

def ing2e(word):
    """AUX function to help Snowballstemmer fix -ing words"""
    if word.endswith("ing"):
        word = word[:-3]+"e"
    return word

def stem_words(tokens):
    from nltk import stem
    snowball = stem.SnowballStemmer("norwegian")
    tokens = [snowball.stem(i) for i in tokens]
    return [ing2e(i) for i in tokens]

def tokenize_remove_stopwords_snowballstem(text):
    '''uses the snowballstemmer'''
    words = nltk.wordpunct_tokenize(text)# text.decode('utf8') # returns list
    # remove stopwords
    words = remove_stopwords(words)
    # and do some stemming
    words = stem_words(words)
    return " ".join(words)
#some tests
#
# t1 = "15 Men Gud skal lære dem å drive ap! Han vil la dem ture frem i deres oppsetsighet på deres blinde ferd."
# t11 = "15 Men Gud skal lære dem å drive ap! Han vil la dem ture frem i deres oppsetsighet på deres blinde ferd.".decode("utf8")
# t2 = """16 De har kjøpt villfarelse for rettlednings pris. Men dette er en dårlig handel, og de er ikke på rett
# vei."""
# t3 = """17 De kan sammenlignes med at noen tenner opp ild, men når den lyser opp, tar Gud deres lys bort
# og lar dem sitte i mørket uten å se. """
# t4 = "18 Døve, stumme, blinde, finner de ingen vei tilbake."
# t5 = """19 Eller, det er som om det var i et skybrudd fra oven, med mørke, torden og lyn. De putter fingrene
# i ørene for tordenen, livende redde. Gud har makt over de vantro."""
#t6 = "Gunnar og Gunn har navnedag i dag og løper. De liker løping. Og delfiner. Navnene er norrøne. Gunn &#8211;  som er et forledd i mange norrøne navn, kommer fra ordet gunnr som betyr strider, kamper.".decode("utf8")
#t7 = "vart over også skal hele andre gang vere dere henne alle, Eirik er her".decode("utf8")
#ttt = "løping var det siste de hadde ønsket seg. fiskerne bodde i båtene sine alle høsten".decode("utf8")
#print tokenize_remove_stopwords_stem(ttt)
# print "*"*10
# print t7
# print tokenize_remove_stopwords(t7)
# print "*"*10
# print t6
# print tokenize_remove_stopwords(t6)
# #print tokenize_remove_stopwords(t1)
# print "*"*10
# print t11
# print " ".join(remove_stopwords(nltk.wordpunct_tokenize(t11)))
# print " ".join(tokenize_remove_stopwords(t11))
# # ekte_text = u"""Invitasjon til pressefrokost: Turiståret 2013 - Utsiktene for 2014 - Resultater fra Turistundersøkelsen 2013 Seniorrådgiver reiseliv
# #
# # Norge tapte markedsandeler i 2013 og spesielt stor var nedgangen fra viktige markeder som Tyskland og Nederland. Nå viser også Innovasjon Norges vinterprognoser en avventende holdning fra reiselivsaktørene. Kan en svekket norsk krone bidra til å snu de negative reiselivstrendene i 2014?
# #       Vi ser en positiv vekst i antall asiatiske gjestedøgn. Om denne trenden fortsetter vil asiatiske gjestedøgn om 10 år utgjøre en like stor andel hotellovernattinger i Norge som eurolandene utgjør i dag.
# #       Det globale turistmarkedet er i store endringer, og Norge må jobbe hardt for å ta en større del av markedsandelene i årene som kommer. En svekket norsk krone kan få en positiv betydning for reiselivsåret i 2014. Men hva skal til for å trekke flere turister til Norge og hvordan skal Innovasjon Norge lede markedsføringen av Norge i 2014?
# #       Påmelding: Da vi serverer frokost er det fint om alle melder seg på. Det gjøres ved å sende en e-post til morav@innovasjonnorge.no       
# #       Kontaktperson i Innovasjon Norge
# #       Mona Raa Ravndal
# #       Telefon: 942 94 04
# #       Mobiltelefon: 942 94 04
# #       E-post: morav@innovasjonnorge.no
# #         **** Dette stoff formidler NTB for andre - se www.ntbinfo.no ****
# #         """
#
#
#
# # tokens =  ["flyndre","flyndrer", "kingler", 'saksing',"flokker", u"løping", "krangling", "sykling","hosting", u"spøke", u"løper"]
# # tokens = [u"løping",u"løping",u"løping",u"løping",u"løping",u"løping",u"løping"]
# #
# #
# # ekte_text = [w for w in ekte_text.split() if not w in stoppord]
# #
# # print ekte_text
# # print stem_words(tokens)
# # print type(stem_words(tokens)[5])
