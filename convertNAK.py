#!/usr/bin/python2.7
# coding: utf-8
import os
import sys
#sys.setdefaultencoding("utf-8")
from ntb_codes import iptc_codes
walk_dir = sys.argv[1]

from time import time
from lxml import html
from lxml import etree
from urllib import quote
import urllib2
from hashlib import sha1

import time
start = time.time()

from text_functions import tokenize_remove_stopwords, tokenize_remove_stopwords_stem

def isInt(val):
    return val == int(val)

failed_docs = 0
has_category = 0
estimated_nr_of_result_docs = 0
has_no_main_cat = 0
doc_teller = 0
ntb_id_list = []


def find_text_and_subjects(newsml_content):

    #First parse of the document as XML for the structured attributes
    try:
        xtree = etree.ElementTree(etree.fromstring(newsml_content.encode('utf-8')))
    except:
        global failed_docs
        failed_docs+=1
        print "doc failed to be read, now total: %s. file: %s. Teller: %s" % (failed_docs, filename, doc_teller)
        return

    #print newsml_content
    #print xtree

    if (xtree.findall("//attribute[@name='class1']")):
        global has_category
        has_category+=1

        # Then use HTML parser to find the that looks like HTML hence can leverage
        # the text_content method.
        html_tags=['div'] #'hedline', 'body.content', 'tagline',
        htree = etree.ElementTree(html.document_fromstring(newsml_content.encode('utf-8')))
        text_items = [e.text_content().strip()
                       for tag in html_tags
                       for e in htree.findall('//' + tag)]
        text = "\n\n".join(text_items)
        #print text[:100] + " [...]"


        if (htree.xpath(".//attribute[@name='class1']/@value")):


            ## NB: hvis denne er tom, så legres doc i rota
            # we have a categori
            main_cat = htree.xpath(".//attribute[@name='class1']/@value")[0].replace(',', '_')

            # if we have no proper cat, skip
            if (main_cat.strip()=="" or main_cat is None or main_cat.startswith("_")) :
                return
            if (main_cat.startswith("lokalt")):
                return


            non_semantic = ["2014", "a", "innenriks", "internasjonal", "iriks","2div1","2div3","2div4",
                            "baksiden", "bakforsiden", "nyheter_ lokalt", "eliteserien", "nyheter_dbtv",
                            "nyheter_innenriks", "nyheter_utenriks", "nyheter_iriks", "nyheter_uriks",
                            "nyheter_lokalt", "nyheter", "nyheter_trondheim", "osloby_nyheter",
                            "nyheter_ lokalt_ stavanger", "nyheter_ utenriks", "nyheter_sortrondelag",
                            "mening"]
            if (main_cat in non_semantic):
                return # this does not tell us anythin, skip

            sport_cats = ["d2_Sport", "d2_Fotball","magasinet_Sport", "nyheter_Fifa"]
            if (main_cat in sport_cats):
                main_cat = "sport"

            kultur_cats = ["d2_Anmeldt", "d2_Arkitektur", "d2_Design", "d2_Film", "d2_Fotografi", "d2_Kultur",
                            "d2_Kunst", "d2_Litteratur", "d2_Mote", "d2_Musikk", "d2_Tegneserie"]
            if (main_cat in kultur_cats):
                main_cat = "kultur"

            sci_tech_cats = ["d2_Forskning","magasinet_Teknologi"]
            if (main_cat in sci_tech_cats):
                main_cat = "sci_tech"

            mat_vin_cats = ["vinguiden", "mat"]
            if (main_cat in mat_vin_cats):
                main_cat = "mat_vin"

            okonomi_cats = ["forbruker_bank", "forbruker_boligmarkedet", "forbruker_din-oekonomi",
                            "forbruker_fiskeri", "innenriks_ okonomi"]
            if (main_cat in okonomi_cats):
                main_cat = "okonomi"

            politikk_cats = ["innenriks_ politikk", "innenriks_politikk","magasinet_Politikk"]
            if (main_cat in politikk_cats):
                main_cat = "politikk"

            vaer_cats = ["innenriks_var_og_uvar"]
            if (main_cat in vaer_cats):
                main_cat = "vaer"

            # remove debate-stuff
            if (main_cat.startswith("nyheter_Kommentar") or main_cat.startswith("kommentar") or main_cat.startswith("nyheter_meninger") or main_cat.startswith("kultur_debatt") or main_cat.startswith("kultur_kommentar") or main_cat.startswith("kultur_kronikk") or main_cat.startswith("kultur_meninger") or main_cat.startswith("debatt")):
                return # this is just too vide, as all debates on all topics are here.., skip

            if (main_cat.startswith("kultur_")):# this is a whole lot.
                main_cat = "kultur" #remember to remove debate-orented culture before this point..
            elif (main_cat.startswith("bergenpuls_restaurant")): # bergenpul er kultu
                main_cat = "mat_vin"
            elif (main_cat.startswith("bergenpuls")): # bergenpul er kultu
                main_cat = "kultur"
            elif (main_cat.startswith("sport") or main_cat.startswith("100Sport")):
                main_cat = "sport"
            elif (main_cat.startswith("bil_") or main_cat.startswith("tema_klikk_bil")):
                main_cat = "bil"
            elif (main_cat.startswith("dnaktiv_")):
                main_cat = "dnaktiv"
            elif (main_cat.startswith("energi_")):
                main_cat = "energi"
            elif (main_cat.startswith("fotball")):
                main_cat = "sport"
            elif (main_cat.startswith("jobb_")):
                main_cat = "jobb"
            elif (main_cat.startswith("jobbledelse")):
                main_cat = "jobbledelse"
            elif (main_cat.startswith("jul_") or main_cat.startswith("nyheter_jul")):
                main_cat = "jul"
            elif (main_cat.startswith("kjendis")):
                main_cat = "kjendis"
            elif (main_cat.startswith("matvin_")):
                main_cat = "mat_vin"
            elif (main_cat.startswith("mening")): # this is more debate stuff
                main_cat = "mening" # or just remove?
            elif (main_cat.startswith("musikk") or main_cat.startswith("nyheter_musikk")):
                main_cat = "kultur"
            # elif (main_cat.startswith("nyheter_ lokalt")): # dette er jo umulig å klassifisere.
            #     main_cat = "nyheter_lokalt"
            elif (main_cat.startswith("nyheter_22_juli") or main_cat.startswith("nyheter_innenriks_22_juli")):
                main_cat = "terror_22juli"
            elif (main_cat.startswith("nyheter_innenriks_anders_behring_") or main_cat.startswith("nyheter_breivik")):
                main_cat = "terror_abb"
            elif (main_cat.startswith("nyheter_innenriks_breivik") or main_cat.startswith("nyheter_anders_behring_breivik")):
                main_cat = "terror_abb"
            elif (main_cat.startswith("nyheter_breivik_anders_behring")):
                main_cat = "terror_abb"
            elif (main_cat.startswith("nyheter_arbeidsliv")):
                main_cat = "arbeidsliv"
            elif (main_cat.startswith("nyheter_arkeologi_forskning")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_astronomi")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_drap")):
                main_cat = "krim_drap"
            elif (main_cat.startswith("nyheter_innenriks_drap")):
                main_cat = "krim_drap"
            elif (main_cat.startswith("nyheter_ekstremver") or main_cat.startswith("nyheter_innenriks_uver")):
                main_cat = "vaer"
            elif (main_cat.startswith("nyheter_film") or main_cat.startswith("nyheter_litteratur")):
                main_cat = "kultur"
            elif (main_cat.startswith("nyheter_finans")):
                main_cat = "okonomi"
            elif (main_cat.startswith("nyheter_flom")):
                main_cat = "vaer"
            elif (main_cat.startswith("nyheter_fly")):
                main_cat = "transport"
            elif (main_cat.startswith("nyheter_forbruker")):
                main_cat = "forbruker"
            elif (main_cat.startswith("nyheter_forskning")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_forsvar")):
                main_cat = "politikk" # er dette riktig?
            elif (main_cat.startswith("nyheter_fritid")):
                main_cat = "fritid"
            elif (main_cat.startswith("nyheter_handel")):
                main_cat = "okonomi"
            elif (main_cat.startswith("nyheter_hegnarno")):
                main_cat = "okonomi"
            elif (main_cat.startswith("nyheter_forbruker")):
                main_cat = "forbruker"
            elif (main_cat.startswith("nyheter_innenriks_helse") or main_cat.startswith("tema_klikk_helse")):
                main_cat = "helse"
            elif (main_cat.startswith("nyheter_innenriks_krim") or main_cat.startswith("nyheter_krim")):
                main_cat = "krim"
            elif (main_cat.startswith("nyheter_innenriks_politikk")):
                main_cat = "politikk"
            elif (main_cat.startswith("nyheter_innenriks_ran")):
                main_cat = "krim"
            elif (main_cat.startswith("nyheter_innenriks_terror")):
                main_cat = "terror"
            elif (main_cat.startswith("nyheter_innenriks_trafikk")):
                main_cat = "trafikk" # mye ulkker naturligvis
            elif (main_cat.startswith("nyheter_innenriks_valg") or main_cat.startswith("nyheter_meningsmalinger")):
                main_cat = "politikk"
            elif (main_cat.startswith("nyheter_innenriks_ver_")):
                main_cat = "vaer"
            elif (main_cat.startswith("nyheter_innenriks_veret")):
                main_cat = "vaer"
            elif (main_cat.startswith("nyheter_innenriks_vold")):
                main_cat = "krim" # eller
            elif (main_cat.startswith("nyheter_jule")):
                main_cat = "jul"
            elif (main_cat.startswith("nyheter_konge")):
                main_cat = "kongehus"
            elif (main_cat.startswith("nyheter_krig_og_konflikter")):
                main_cat = "krig"
            elif (main_cat.startswith("nyheter_kuriosa")):
                main_cat = "kuriosa"
            elif (main_cat.startswith("nyheter_mat_") or main_cat.startswith("tema_mat")):
                main_cat = "mat_vin" # og drikke?
            elif (main_cat.startswith("nyheter_landbruk")):
                main_cat = "landbruk"
            elif (main_cat.startswith("nyheter_naringsliv")):
                main_cat = "okonomi"
            elif (main_cat.startswith("nyheter_narkotika")):
                main_cat = "krim"
            elif (main_cat.startswith("nyheter_nobel")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_okonomi") or main_cat.startswith("tema_okonomi")):
                main_cat = "okonomi"
            elif (main_cat.startswith("nyheter_politi_")):
                main_cat = "politi"
            elif (main_cat.startswith("nyheter_politiet")):
                main_cat = "politi"
            elif (main_cat.startswith("nyheter_politikk")): # dette fanger muligens opp for mye
                main_cat = "politikk"                       # innenriks, utenriks, helse....
            elif (main_cat.startswith("nyheter_politikk_krig_og_konflikter")):
                main_cat = "krig"
            elif (main_cat.startswith("nyheter_politiske_partier")):
                main_cat = "politikk"
            elif (main_cat.startswith("nyheter_ran") or main_cat.startswith("nyheter_innenriks_tyveri") or main_cat.startswith("nyheter_tyveri")):
                main_cat = "krim_ran_tyveri"
            elif (main_cat.startswith("nyheter_rettssaker") or main_cat.startswith("nyheter_knivstikking")):
                main_cat = "krim"
            elif (main_cat.startswith("nyheter_romfart")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_samferdsel")):
                main_cat = "samferdsel"
            elif (main_cat.startswith("nyheter_samfunn_politikk")):
                main_cat = "politikk"
            elif (main_cat.startswith("nyheter_samfunn_valg")):
                main_cat = "politikk"
            elif (main_cat.startswith("nyheter_seksualforbrytelser")):
                main_cat = "krim_sex"
            elif (main_cat.startswith("nyheter_skatt")):
                main_cat = "skatt" # politikk eller økonomi? skattelister, stakkeetaten, skatteoppgjør, skatteundragelser..
            elif (main_cat.startswith("nyheter_skogbrann") or main_cat.startswith("nyheter_innenriks_brann")):
                main_cat = "branner"
            elif (main_cat.startswith("nyheter_skole")):
                main_cat = "skole"
            elif (main_cat.startswith("nyheter_smug") or main_cat.startswith("nyheter_innenriks_smugling")):
                main_cat = "krim_smugling"
            elif (main_cat.startswith("nyheter_statoil")):
                main_cat = "statoil"
            elif (main_cat.startswith("nyheter_statsbudsjett")or main_cat.startswith("nyheter_innenriks_statsbudsjett")):
                main_cat = "okonomi_stadsbudsjett"
            elif (main_cat.startswith("nyheter_streik")):
                main_cat = "arbeidsliv"
            elif (main_cat.startswith("nyheter_sykdom")):
                main_cat = "helse"
            elif (main_cat.startswith("nyheter_teknologi")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_terror")):
                main_cat = "terror"
            elif (main_cat.startswith("nyheter_tog")):
                main_cat = "samferdsel"
            elif (main_cat.startswith("nyheter_trafikk")): # fanger mye
                main_cat = "trafikk"
            elif (main_cat.startswith("nyheter_utdanning")):
                main_cat = "utdanning"
            elif (main_cat.startswith("nyheter_valg")):
                main_cat = "politikk"
            elif (main_cat.startswith("nyheter_ver_")):
                main_cat = "vaer"
            elif (main_cat.startswith("nyheter_verdensrommet")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_veret_")):
                main_cat = "vaer"
            elif (main_cat.startswith("nyheter_vermelding")):
                main_cat = "vaer"
            elif (main_cat.startswith("nyheter_viten")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_vold")):
                main_cat = "vold"
            elif (main_cat.startswith("okonomi_bedrift")):
                main_cat = "okonomi"
            elif (main_cat.startswith("rampelys")): #alltid kultur, right?
                main_cat = "kultur"
            elif (main_cat.startswith("tema_bil_")):
                main_cat = "bil"
            elif (main_cat.startswith("tema_reise_")):
                main_cat = "resiseliv" #ferie, eller transport, samferdsel? ser ut il å være mest ferie-livsstil
            elif (main_cat.startswith("tema_tekno")):
                main_cat = "tekno" # er dette sci_tech, eller forbruker eller.no?
            elif (main_cat.startswith("forbruker_bil")):
                main_cat = "bil"
            elif (main_cat.startswith("forbruker_helse")):
                main_cat = "forbruker_helse"
            elif (main_cat.startswith("forbruker_reise")):
                main_cat = "forbruker_reise"
            elif (main_cat.startswith("forbruker_teknologi")):
                main_cat = "forbruker_teknologi"
            elif (main_cat.startswith("gasellene")):
                main_cat = "okonomi_gasellene"
            elif (main_cat.startswith("nyheter_17")):
                main_cat = "17mai"
            elif (main_cat.startswith("nyheter_22")):
                main_cat = "terror_22juli"
            elif (main_cat.startswith("nyheter_apple")):
                main_cat = "sci_tech" # eller forbruker??
            elif (main_cat.startswith("nyheter_bilulykke")):
                main_cat = "bilulykker"
            elif (main_cat.startswith("nyheter_biologi")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_bors")):
                main_cat = "okonomi"
            elif (main_cat.startswith("nyheter_brann")): # dette ser heldigvis ikke ut til å treffe fotball fra bergen
                main_cat = "branner"
            elif (main_cat.startswith("nyheter_data")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_dyr") or main_cat.startswith("nyheter_utenriks_dyr")):
                main_cat = "dyr" # pussig at dett er en greie..
            elif (main_cat.startswith("nyheter_ebola")):
                main_cat = "ebola"
            elif (main_cat.startswith("nyheter_eu")):
                main_cat = "nyheter_eu"
            elif (main_cat.startswith("nyheter_fisk_")):
                main_cat = "dyr"
            elif (main_cat.startswith("nyheter_fotball_")):
                main_cat = "sport"
            elif (main_cat.startswith("nyheter_helse_")):
                main_cat = "helse"
            elif (main_cat.startswith("nyheter_innenriks_dodsfall")):
                main_cat = "dodsfall"
            elif (main_cat.startswith("nyheter_innenriks_dyr")):
                main_cat = "dyr"
            elif (main_cat.startswith("nyheter_innenriks_fly")):
                main_cat = "fly"
            elif (main_cat.startswith("nyheter_innenriks_forskning") or main_cat.startswith("nyheter_utenriks_forskning")):
                main_cat = "sci_tech"
            elif (main_cat.startswith("nyheter_innenriks_knivstikking")):
                main_cat = "kriminalitet"
            elif (main_cat.startswith("nyheter_innenriks_leteaksjon") or main_cat.startswith("nyheter_leteaksjon")):
                main_cat = "leteaksjoner"
            elif (main_cat.startswith("nyheter_innenriks_narkotika")):
                main_cat = "krim_narko"
            elif (main_cat.startswith("nyheter_innenriks_okonomi")):
                main_cat = "okonomi"
            elif (main_cat.startswith("nyheter_innenriks_overgrep") or main_cat.startswith("nyheter_overgr")):
                main_cat = "krim_overgrep"
            elif (main_cat.startswith("nyheter_innenriks_politi") or main_cat.startswith("nyheter_politi")): # dette er nok noe politikk
                main_cat = "politi" # men stort sett krim
            elif (main_cat.startswith("nyheter_innenriks_rettssak")):
                main_cat = "krim_rettsak"
            elif (main_cat.startswith("nyheter_innenriks_samfunn_politikk") or main_cat.startswith("nyheter_utenriks_politikk")):
                main_cat = "politikk"
            elif (main_cat.startswith("nyheter_innenriks_samfunn_valg")):
                main_cat = "politikk_valg"
            elif (main_cat.startswith("nyheter_innenriks_skyt") or main_cat.startswith("nyheter_skyt") or main_cat.startswith("nyheter_utenriks_skyting")):
                main_cat = "krim_skyting"
            elif (main_cat.startswith("nyheter_innenriks_ulykke") or main_cat.startswith("nyheter_ulykke")):
                main_cat = "ulykker"
            elif (main_cat.startswith("nyheter_jordskjelv")):
                main_cat = "jordskjelv"
            elif (main_cat.startswith("nyheter_kidnap")):
                main_cat = "krim_kidnapping"
            elif (main_cat.startswith("nyheter_ras")):
                main_cat = "ras"
            elif (main_cat.startswith("nyheter_samfunn_innenriks_politikk")):
                main_cat = "politikk"
            elif (main_cat.startswith("turer")):
                main_cat = "turer"
            # elif (main_cat.startswith("nyheter_kidnap")):
            #     main_cat = "krim_kidnapping"
            # elif (main_cat.startswith("nyheter_kidnap")):
            #     main_cat = "krim_kidnapping"
            # elif (main_cat.startswith("nyheter_kidnap")):
            #     main_cat = "krim_kidnapping"
            # elif (main_cat.startswith("nyheter_kidnap")):
            #     main_cat = "krim_kidnapping"
            # elif (main_cat.startswith("nyheter_kidnap")):
            #     main_cat = "krim_kidnapping"
            # elif (main_cat.startswith("nyheter_kidnap")):
            #     main_cat = "krim_kidnapping"
            # elif (main_cat.startswith("nyheter_kidnap")):
            #     main_cat = "krim_kidnapping"
            # elif (main_cat.startswith("nyheter_kidnap")):
            #     main_cat = "krim_kidnapping"
            # elif (main_cat.startswith("nyheter_kidnap")):
            #     main_cat = "krim_kidnapping"
            # take thise with a space in them last, unsure if they cath * or too much
            elif (main_cat.startswith("nyheter_ okonomi")):
                main_cat = "okonomi"
            elif (main_cat.startswith("nyheter_ politikk") or main_cat.startswith("nyheter_iriks_politikk")):
                main_cat = "politikk"

                            # # we need to overstear NTB with Hells cats
            # # but I save this for later, to use Helles brilliant mind to categorize the categories
            # # samfunsspørsmål = arbeidsliv + nedisun&helse + natur&miljø + religion&livssyn + sosiale forhold + utdanning
            # if (main_cat=="ARB" or main_cat=="MED" or main_cat=="NAT" or main_cat=="REL" or main_cat=="SOS" or main_cat=="UTD"):
            #     main_cat ="SAMF"
            # # politikk = politikk + krig
            # if (main_cat=="KRI" or main_cat=="POL"):
            #     main_cat ="POLI"
            # # Kultur = Kultur&underholdning + fritid + kuriosa&kjendisser
            # if (main_cat=="KUL" or main_cat=="FRI" or main_cat=="KUR"):
            #     main_cat ="KULT"

            # now create folders
            if not os.path.exists('./nak_data_collapsed_stemmed'):            # create data folder if not exists
                os.makedirs('./nak_data_collapsed_stemmed')
            if not os.path.exists('./nak_data_collapsed_stemmed/'+main_cat+'/'):     # create data/sport folder is not exist
                os.makedirs('./nak_data_collapsed_stemmed/'+main_cat+'/')

            # Can set colors for folder if I want..
            # from xattr import xattr
            # def set_label(filename, color_name):
            #     colors = ['none', 'gray', 'green', 'purple', 'blue', 'yellow', 'red', 'orange']
            #     key = u'com.apple.FinderInfo'
            #     attrs = xattr(filename)
            #     current = attrs.copy().get(key, chr(0)*32)
            #     changed = current[:9] + chr(colors.index(color_name)*2) + current[10:]
            #     attrs.set(key, changed)
            #
            # set_label('/Users/chbrown/Desktop', 'green')


            try:
                with codecs.open(os.path.join('./nak_data_collapsed_stemmed/'+main_cat+'/',filename), "w", "utf-8-sig") as F:  # http://stackoverflow.com/questions/934160/write-to-utf-8-file-in-python
                    text_u_stop = tokenize_remove_stopwords_stem(text)
                    F.write(text_u_stop)
            except:  # OSError
                print('Writing file failed')
        else:
            print "denne har ikke kategori, dette har enda ikke skjedd"
            has_no_main_cat+=1
            #sys.exit(0)




# start.




print('walk_dir = ' + walk_dir)

# If your current working directory may change during script execution, it's recommended to
# immediately convert program arguments to an absolute path. Then the variable root below will
# be an absolute path as well. Example:
# walk_dir = os.path.abspath(walk_dir)
print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

for root, subdirs, files in os.walk(walk_dir):
    print('--\nroot = ' + root)
    #list_file_path = os.path.join(root, 'my-directory-list.txt')
    #print('list_file_path = ' + list_file_path)

    #with open(list_file_path, 'wb') as list_file:
    for subdir in subdirs:
        print('\t- subdirectory ' + subdir)


    for filename in files:
        file_path = os.path.join(root, filename)
        #print('\t- file %s (full path: %s)' % (filename, file_path))
        #print('\t- %s' % (filename))


        # 1. now I first just want to find the elements of the NTB files

        if not filename.endswith('.xml'): # skip .DStore
            continue # meaning skipping this iteration

        doc_teller+=1

        import codecs
        encodings = ['utf-8', 'iso-8859-1'] # ,'windows-1250', 'windows-1252'
        for e in encodings:
            try:
                fh = codecs.open(file_path, 'r', encoding=e)
                fh.readlines()
                fh.seek(0)
            except UnicodeDecodeError:
                print('\t- got unicode error with %s , trying different encoding' % e)
            else:
                #print('\t- (%s) opening the file %s with encoding:  %s ' % (doc_teller,file_path,e))
                find_text_and_subjects(fh.read())
                break #continue
        #newsml_content = open(file_path, 'rb').read()

        # 2. then store them in folders acording to cateories.
        # this is done in the find_text_and_subjects() function, this function
        # should probably just be removed as linear code where it is run...

print "doc_teller: %s" % (doc_teller)
print "failed_docs: %s" % (failed_docs)
print "has no main news cat: %s" % (has_no_main_cat)
print "has_category: %s" % (has_category)
print "estimated_nr_of_result_docs: %s" % (estimated_nr_of_result_docs)
print 'It took', time.time()-start, 'seconds.'
print "Length of ntb_id_list: %s" % (len(ntb_id_list))
