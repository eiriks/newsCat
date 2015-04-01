#!/usr/bin/python2.7
# coding: utf-8
import os
import sys
from time import time
from lxml import html
from lxml import etree
import codecs
import json
import time
#from ntb_codes import iptc_codes # NTB codes are not relevant for NAK
from text_functions import tokenize_remove_stopwords, tokenize_remove_stopwords_stem

start = time.time()

def isInt(val):
    return val == int(val)

failed_docs = 0
has_category = 0
estimated_nr_of_result_docs = 0
has_no_main_cat = 0
doc_teller = 0
ntb_id_list = []

walk_dir = sys.argv[1] # first argument on command line is the folder with data (subfolders are ok)
OUT_FOLDER = './nak_data_collapsed_stemmed'

# function to color code folders in osx
from xattr import xattr
def set_label(filename, color_name):
    colors = ['none', 'gray', 'green', 'purple', 'blue', 'yellow', 'red', 'orange']
    key = u'com.apple.FinderInfo'
    attrs = xattr(filename)
    current = attrs.copy().get(key, chr(0)*32)
    changed = current[:9] + chr(colors.index(color_name)*2) + current[10:]
    attrs.set(key, changed)



def find_text_and_subjects(newsml_content):
    main_cat_altered = False
    #First parse of the document as XML for the structured attributes
    try:
        xtree = etree.ElementTree(etree.fromstring(newsml_content.encode('utf-8')))
    except:
        global failed_docs
        failed_docs+=1
        print "doc failed to be read, now total: %s. file: %s. Teller: %s" % (failed_docs, filename, doc_teller)
        return

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

        if (htree.xpath(".//attribute[@name='class1']/@value")):
            # we have a categori
            main_cat = htree.xpath(".//attribute[@name='class1']/@value")[0].split(",")#.replace(',', '_')
            main_cat = [w.strip().lower() for w in main_cat]
            # recreate labels by ordering accoring to: cnt
            sorted_cats = sorted(main_cat, key=cnt.__getitem__, reverse=True)
            # remove keywords only used once
            # this is mainly sections in the paper, not categories and they are too big
            non_semantic = ["2014", "a", "innenriks", "internasjonal", "iriks","2div1","2div3","2div4",
                            "baksiden", "bakforsiden", "lokalt", "eliteserien", "dbtv",
                            "uriks", "nyheter", "tema", "utenriks", "klikk","meninger", "kommentar",
                            "debatt", "blogg","magasinet","magasin", "kk", "aller", "dinside", "osloby",
                            "etterbors", "hegnarno", "bolig", "d2", "dagbladet", "dnaktiv",
                            "dokumentar", "privat", "eiendom", "forbruker", "gasellene",
                            "god_torsdag", "lillesand", "det_beste", "leder", "motor", "nyhet",
                            "nytte", "samfunn", "talent", "bergenpuls", "kronikker", "kommentarer",
                            "kommentatorer","inne_og_ute", "is", "medier", "utenriks_ntb", "innenriks_ntb",
                            "verden", "video", "kronikk", "spaltister", "idag", "dnlordag",
                            "nye-inntrykk_portrett", "tablet_forside", "ideer", "incomming", "btmagasinet"]
            # places that do not describe the categories of the stories
            steder = ["norge", "trondheim", "sverige", "storbritania", "stavanger",
                            "spania", "russland", "kina", "japan", "italia", "israel", "palestina",
                            "gaza", "island", "iran", "india", "frankrike", "england", "australia",
                            "egypt", "bergen", "afghanistan", "afrika", "algerie", "argentina", "brasil", "canada",
                            "danmark", "boston", "kommune", "canada", "colombia", "dubai", "filippinene",
                            "finnmark", "hamar", "haugesund", "hedmark", "hellas", "irak", "jemen",
                            "kenya", "kongo", "kristiansand", "kristiansund", "larvik", "libya", "london",
                            "mexico", "midtosten", "moss", "narvik", "nederland", "new_york",
                            "new_zealand", "nigeria", "nord-korea","nord_korea", "nordkorea",
                            "nord-irland", "os", "oslo", "pakistan", "paris", "peru", "russland",
                            "sandnes", "sarpsborg", "sarajevo", "skottland", "sola", "somalia",
                            "sor_afrika", "sor_afrika", "sor_korea", "sor-korea","sor-sudan",
                            "sor-trondelag","sortrondelag", "spania", "stavanger", "storbritania",
                            "sudan", "svalbard", "sverige", "syria", "telemark", "texas",
                            "thailand", "tonsberg", "troms", "tromso", "trondheim", "tyrkia",
                            "tyskland", "ukraina", "usa", "voss", "zimbabwe", "irland",
                            "agder", "alesund", "antarktis", "fredrikstad", "drammen", "lofoten",
                            "mali", "mandal", "molde", "portugal", "sor-afrika", "stockholm",
                            "storbritannia", "sveits", "taiwan", "nordtrondelag", "jaeren",
                            "amagasinet", "aust_agder", "ryfylke", "moreromsdal", "midtosten",
                            "nordfylket", "sogne", "vennesla", "setesdal", "stjordal", "oppdal",
                            "cuba", "usbekistan", "belgia", "sirdal", "solarandaberg", "stjordal" ]
            # add places to non_semantic
            non_semantic.extend(steder)
            # slom down the main_cat list by removing rare words and non semantic words
            slim_fit = [w for w in sorted_cats if cnt[w]>2 and w not in non_semantic]
            main_cat = "_".join(slim_fit) # make it a string
            # if we have no proper cat, skip
            if (main_cat.strip()=="" or main_cat is None or main_cat.startswith(("_", 'nyemeninger'))) :
                return

            # here I collapse frequently used keywords into more general categories
            if main_cat.startswith(("100sport","sport","sjakk","fotball","boksing","doping",
                "langrenn","friidrett","idrett","handball","volleybal","ishockey","skoyter",
                "tennis", "landslaget", "loping", "maraton", "petter_northug", "roing",
                "sykling", "trav", "norwaychess")):
                main_cat = "sport"
                main_cat_altered = True # so I know I want to color code this when it becomes a folder
            elif main_cat.startswith("17_mai"):
                main_cat = "17mai"
                main_cat_altered = True
            elif main_cat.startswith(("privatokonomi", "okonomi","naringsliv","neringsliv","naring",
                "finans","handel", "varehandel", "aksje", "bank", "bolig","bors","dinepenger","dnb",
                "energi", "gass","olje","hval", "hotell", "industri", "invest", "it", "jobbledelse",
                "jordbruk", "landbruk","konkurs", "kreditt", "laks", "makro", "naeringsliv",
                "netthandel", "norwegian_", "sas_", "telenor","penger", "renta", "rente", "shipping",
                "statoil", "xxl","yara","streik", "turisme", "valuta", "wall-street", "brskommentar",
                "aker-solutions")):
                main_cat = "okonomi_naering"
                main_cat_altered = True
            elif main_cat.startswith(("kriminalitet", "krim_", "kidnapping", "narko",
                "organisert_kriminalitet", "bortforing", "forsvinning", "gissel", "gjeng", "hack",
                "kokain", "mafia", "mishandling", "mistenkelig")):
                main_cat = "krim"
                main_cat_altered = True
            elif main_cat.startswith(("voldtekt","overgrep","overgrip","seksualforbrytels",
                "prostitusjon", "rune_oygard", "seksuelle_", "seksuelt_", "sexhandel",
                "sexkjo", "trafficking")):
                main_cat = "krim_seksualforbrytelser_prostitusjon"
                main_cat_altered = True
            elif main_cat.startswith(("vold","drap","kniv", "overfall", "seriemord")):
                main_cat = "krim_vold_drap_kniv"
                main_cat_altered = True
            elif main_cat.startswith(("korrupsjon", "hvitvasking", "okokrim", "svindel", "bedrageri",
                "underslag")):
                main_cat = "krim"
                main_cat_altered = True
            elif main_cat.startswith(("trusler", "tyv","ran_", "innbrudd")):
                main_cat = "krim_trusler"
                main_cat_altered = True
            elif main_cat.startswith(("politi_","politiaksjon","politiet", "politiets", "pst_",
                "politijakt", "eirik_jensen", "kripos", "pst", "politiloggen", "politimester",
                "politivold")):
                main_cat = "krim_politi"
                main_cat_altered = True
            elif main_cat.startswith(("tiltale","siktelse","rettssak","rettsak","rettssal","fengsel","etterforskning",
                "dom_", "varetekt", "fengsling", "hoyesterett", "pagripelse", "siktet", "straff")):
                main_cat = "krim_rettegang"
                main_cat_altered = True
            elif main_cat.startswith(("smugling","menneskehandel")):
                main_cat = "krim_smugling_menneskehandel"
                main_cat_altered = True
            elif (main_cat.startswith("skyt")):
                main_cat = "krim_skyt"
                main_cat_altered = True
            elif main_cat.startswith(("drone","krig", "hamas", "tortur","vapen","taliban","isil", "konflikt", "massakre", "nato", "osama")):
                main_cat = "krig_og_konflikt"
                main_cat_altered = True
            elif main_cat.startswith(("viten","verdensrommet","forskning","astronomi","data",
                "nasa","romfart", "universitet", "forsikring", "meteor", "ntnu", "arkeologi",
                "uit", "uib", "uio")):
                main_cat = "sci_tech"
                main_cat_altered = True
            elif main_cat.startswith(("klima", "milj")):
                main_cat = "sci_tech_klima_miljo"
                main_cat_altered = True
            elif main_cat.startswith(("vere", "ver_", "uver","storm","ekstremver","lyn",
                "regn","flom_", "vaer", "tyfon", "tornado", "orkan","flom", "storm", "syklon",
                "tsunami", "vermelding", "vervarsel")):
                main_cat = "vaer"
                main_cat_altered = True
            elif (main_cat.startswith("valg")):
                main_cat = "politikk_valg"
                main_cat_altered = True
            elif main_cat.startswith(("regjering","president","politikk","asyl","eu", "fn", "lo_"
                "innvandring", "kongressen", "storting", "menneskerett", "spionasje", "statsbudsjett")):
                main_cat = "politikk"
                main_cat_altered = True
            elif main_cat.startswith(("rampelys","musikk","litteratur","kultur", "kunst","bok_",
                "arkitektur","boker", "teater", "tegnes", "design", "kjendiser", "konsert",
                "mote", "munch", "rock", "jazz", "scene", "underholdning")):
                main_cat = "kultur_underholdning"
                main_cat_altered = True
            elif main_cat.startswith(("ulykke", "trafikkulykke","togulykke", "dodsulykke",
                "jordskjelv", "ras_", "skred","snoskred", "rasfare", "vulkan", "batulykke", "drukning",
                "eksplosjon", "evakuering", "redningsaksjon","redningaksjon","forlis", "helikopterstyrt", "jordras", "jordskred",
                "naturkatas", "pakjorsel", "scandinavian-star", "scandinavian_star",
                "brann", "skogbrann")):
                main_cat = "ulykker_or_katastrofer"
                main_cat_altered = True
            elif (main_cat.startswith("turer")): # hverdagsliv
                main_cat = "turer"
                main_cat_altered = True
            elif (main_cat.startswith("trafikk")):
                main_cat = "trafikk"
                main_cat_altered = True
            elif main_cat.startswith(("terror", "bombe")): # mye breivik her (og is og al-qaida, etc)
                main_cat = "terror_og_bombetrussler"
                main_cat_altered = True
            elif main_cat.startswith(("tekno", "mobil")): # også forbrukerstoff
                main_cat = "sci_tech_tekno"
                main_cat_altered = True
            elif main_cat.startswith(("sykkel","svomming")):
                main_cat = "sport"
                main_cat_altered = True
            elif main_cat.startswith(("sykdom", "ebola", "hiv","aids","feilbehandling", "syk_",
                "helsevesen", "kreft", "lege", "psykiatri", "psykisk", "psykologi", "sprek","syke",
                "svineinfluensa", "tann", "tobakk", "trening", "tuberkulose", "virus")):
                main_cat = "helse_sykdom" # også trening (positiv helse)
                main_cat_altered = True
            elif (main_cat.startswith("skatt")):
                main_cat = "okonomi_skatt_politikk" # eller politikk?
                main_cat_altered = True
            elif main_cat.startswith("savnet"):
                main_cat = "savnet_saker"
                main_cat_altered = True
            elif main_cat.startswith(("samferdsel", "fly", "luftfart", "gardermoen", "vei",
                "ferge", "ferje", "jernbane", "kollisjon", "nsb_", "parkering", "t-bane", "taxi",
                "tog", "transport", "trikk", "bybanen", "bynane")):
                main_cat = "samferdsel"
                main_cat_altered = True
            elif main_cat.startswith(("mat_", "matvin", "vin_", "mat-", "matog", "restaurant", "det_beste_jeg_vet")):
                main_cat = "mat_vin"
                main_cat_altered = True
            elif main_cat.startswith(("konge","kong_","kronprins", "prins", "dronning")):
                main_cat = "kongestoff"
                main_cat_altered = True
            elif main_cat.startswith(("jule","jul_")):
                main_cat = "jul"
                main_cat_altered = True
            elif (main_cat.startswith("helse_")):
                main_cat = "helse"
                main_cat_altered = True
            elif (main_cat.startswith("nav_")):
                main_cat = "nav"
                main_cat_altered = True
            elif main_cat.startswith(("dyr", "hund", "katt", "ulv", "elg", "elefant", "hai",
                "isbjorn", "tiger", "veps")):
                main_cat = "dyr"
                main_cat_altered = True
            elif main_cat.startswith(("bil","dnbil", "diesel", "elbil", "tesla", "motor")):
                main_cat = "bil_stoff"
                main_cat_altered = True
            elif (main_cat.startswith("arbeids")): # men ikke arbeiderpartiet
                main_cat = "arbeidsliv"
                main_cat_altered = True
            elif main_cat.startswith(("anders_behring", "22_juli", "22juli", "breivik_", "utoya")):
                main_cat = "terror_abb_22juli"
                main_cat_altered = True
            elif main_cat.startswith(("barn", "foreldre","mamma","pappa","skole","lerer",
                "familie","ungdom","mobbing","graviditet","frieri","bryllup", "farskap",
                "penis","naken","fodsel", "ektepar","ekteskap","utroskap" )):
                main_cat = "barn_og_famile"
                main_cat_altered = True
            elif (main_cat.startswith("forsvaret")):
                main_cat = "forsvaret"
                main_cat_altered = True
            elif main_cat.startswith(("kristendom","islam_","livssyn","paske","pave","religion",
                "kirke", "vatikanet", "den_katolske_kirke", "dommedag", "ekstremisme", "jode",
                "overtro", "jehova", "prest", "imam", "scientologi", "sharia")):
                main_cat = "religion_livssyn"
                main_cat_altered = True
            elif main_cat.startswith(("kuriosa","humor", "utrolige", "verdensrekord")):
                main_cat = "kuriosa"
                main_cat_altered = True
            elif (main_cat.startswith("demonstrasjon")):
                main_cat = "demonstrasjon"
                main_cat_altered = True
            elif main_cat.startswith(("dod_","dode","dodsfall","dodsf")):
                main_cat = "dod_dodsfall"
                main_cat_altered = True
            elif main_cat.startswith(("facebook","likestilling", "samliv","sex_","seksualitet","dildo",
                "kjerlighet","abort","homofil","begravelse","fritid","stud",
                "utdann","alkohol", "fattigdom", "fedme","interior", "hytte","hage","ferie",
                "forurensing", "jobb", "karriere", "kjokken", "stue","vedlikehold","kosthold", "kvinne", "livsstil",
                "nobel", "pensjon", "romfolk")):
                main_cat = "sosiale_sporsmaal"
                main_cat_altered = True
            elif (main_cat.startswith("leteaksjon")):
                main_cat = "leteaksjon"
                main_cat_altered = True
            elif main_cat.startswith(("cruise","reise_", "reiseliv", "reisereportas")):
                main_cat = "reise"
                main_cat_altered = True
            elif main_cat.startswith(("gunnar_sonsteby","andre_verdenskrig", "historie_andre_verdenskrig")):
                main_cat = "2_verdenskrig"
                main_cat_altered = True
            elif main_cat.startswith(("rodt","ap_", "sv_", "krf","frp", "sp_", "venstre", "hoyre",
                "arbeiderpartiet", "senterpariet", "hoeyre",
                "erna_solberg","jens_stoltenberg", "eskil_pedersen", "barack_obama", "eva_joly",
                "fabian_stang","jonas_gahr_store", "kim_jon", "martin_kolberg", "mitt_romney",
                "muammar_kadhafi", "mursi", "nelson_mandela", "obama", "putin","per_sandberg",
                "robert_mugabe", "vladimir_putin", "siv_jensen", "siv-jensen", "stoltenberg",
                "sylvi_listhaug", "trond_giske", "trine_skei_grande")):
                main_cat = "politikk_partier_personer"
                main_cat_altered = True


            # old note:
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

            # here we apply the knowledge of Helle Sjøvaag and collapse even more
            # but now as actual full strings, not "startswith" string
            skal_ut = ["terror_abb_22juli", "22-juli","22-juli_rettssaken","sid", "innsikt_fakta", "nye-inntrykk_reportasje",
                        "nye-inntrykk_portrett", "navn-i-nyhetene", "dyr", "oslopuls", "dalane", "byavisa_tromso",
                        "nye-inntrykk", "annenside", "anbefalinger", "fremtiden", "oslobomben", "nyemeninger_alle_meninger",
                        "nye-inntrykk_lydhort", "lister", "asia_i_dag", "dod_dodsfall", "innsyn", "ordforersaken",
                        "elevavisen", "anmeldt", "forsiden", "snakkut", "godhelg", "forside", "omdal", "innsikt",
                        "idagdiskuterervi", "adressa_noogda", "lordag", "nye-inntrykk_internasjonalen", "2_verdenskrig",
                        "elsters_utfordring", "gjesdal", "forsta", "sirdalagder", "gronn-hverdag", "breivik", "oslosbeste",
                        "pluss", "i_verdens_rikeste_land", "utvalgt", "gudbrandsen", "paper_w8_magasinet", "nav", "siriwo",
                        "wikileaks", "profil", "vendepunktet", "russen", "p-innsiden", "moss-dagblad", "oppdraget",
                        "randaberg", "incoming", "asia-i-dag", "nye-inntrykk_ettertanke", "tv", "islam-debatten",
                        "btbatt", "nord-korea-soer-korea", "rossavik", "medieblikk","bjerkestrand", "oslove", "oslodebatt",
                        "bergensbeste", "norske-helter-2014", "portrettet", "historie", "henvisninger_henvisninger_skjult",
                        "stathelle-mysteriet", "h", "forsvarskuppene", "mening", "byen", "reklame", "p-nattbordet",
                        "oslopuls_stakkarsoss", "eikefjord", "pr", "sexmarkedet", "berserk_jarle_andhoy", "spesial",
                        "sosiale-medier", "bertil_valderhaug", "siste_artikler", "tendens"]
            if main_cat in skal_ut:
                return

            hverdagsliv_super = ["friluftsliv","rengjoring","jaktogfiske","oppussing","nye-inntrykk_bylovene","bo","anmeldelser_restaurant","mat_vin", "vin","reise", "bil_stoff", "barn_og_famile", "trafikk", "vinguiden",
                                "hjem","samferdsel", "mat", "religion_livssyn", "sulten", "jul","paaske", "shopping",
                                "turer", "oppvekst", "oppussing", "adopsjon", "oppvekst_toyen", "sex-og-samliv", "vin"]
            sci_tech_super = ["historie-og-arkeologi","vgdigitaleliv","forskerkaringen","digital", "sci_tech_tekno", "digital_tester"]
            sosiale_sporsmaal_super = ['helse', "helse_sykdom", "arbeidsliv", "sci_tech_klima_miljo", "helse-og-medisin"]
            politikk_super = ["uroen-i-ukraina","nodnett","faktasjekk","usavalget","bashar_al-assad","terror_og_bombetrussler", "norsk-politikk", "krig_og_konflikt", "politikk_valg",
                                "politikk_partier_personer", "usavalg", "forsvaret", "solberg-regjeringen",
                                "demonstrasjon", "kgb_mitrokhin_mitrokhinarkivet", "borgerkrig", "hoeyre"]
            krim_super = ["grensekrim","mona_hoiness_arvestrid_testamente","112","oekonomisk-kriminalitet","sigrid_giskegjerde_schjetne","monika-saken","agnes-saken","jus","leteaksjon","krim_vold_drap_kniv", "krim_politi", "krim_seksualforbrytelser_prostitusjon",
                            "krim_rettegang", "savnet_saker", "krim_trusler", "krim_skyt", "krim_smugling_menneskehandel",
                            "nokas", "ran", "politi-hverdagen", "politi", "kongo-saken_joshua_french_tjostolv_moland"]
            sport_super = ["oslomaraton","nm","hans_petter_jorgensen","norwaychess","spillsenteret", "spillsenter", "spillsenteret_spillsentergammel", "spillsenter_spillsenter"]
            kultur_super = ["kultur_underholdning","bw","17mai","tegnehanne","spraak","bker","oslopuls_oya","kuriosa","film", "film_anmeldelser", "kongestoff", "spill", "oslopuls_kunst_og_scene",
                            "nye-inntrykk_klassisk", "film_oslopuls", "anmeldelser_konsert"]
            okonomi_super = ["formuesskatt","din-oekonomi","din__konomi","oekonomi","gjeldskrisen","n_ringsliv","brskommentar","ledelse","vekstinord","konomi","resultater","okonomi_skatt_politikk", "nringsliv", "okonomi", "oekonomi", "din-oekonomi"]
            vaer_super = ['ver']
            ulykker_og_katastrofer_super = ["vegvesenets-ulykkesrapporter", "ras", "flight-mh370", "helikopterulykke"]

            if main_cat in hverdagsliv_super:
                main_cat = "hverdagsliv"
            elif main_cat in sci_tech_super:
                main_cat = "sci_tech"
            elif main_cat in sosiale_sporsmaal_super:
                main_cat = "sosiale_sporsmaal"
            elif main_cat in politikk_super:
                main_cat = "politikk"
            elif main_cat in krim_super:
                main_cat = "krim"
            elif main_cat in sport_super:
                main_cat = "sport"
            elif main_cat in kultur_super:
                main_cat = "kultur"
            elif main_cat in okonomi_super:
                main_cat = "okonomi_naering"
            elif main_cat in vaer_super:
                main_cat = "vaer"
            elif main_cat in ulykker_og_katastrofer_super:
                main_cat = "ulykker_or_katastrofer"

            # now create folders
            if not os.path.exists(OUT_FOLDER):        # create data folder if not exists
                os.makedirs(OUT_FOLDER)
            if not os.path.exists(OUT_FOLDER+'/'+main_cat+'/'):     # create data/sport folder is not exist
                os.makedirs(OUT_FOLDER+'/'+main_cat+'/')
                if (main_cat_altered):                              # so I know whitch folder are collapsed
                    set_label(OUT_FOLDER+'/'+main_cat, 'purple')

            try:
                with codecs.open(os.path.join(OUT_FOLDER+'/'+main_cat+'/',filename), "w", "utf-8-sig") as F:  # http://stackoverflow.com/questions/934160/write-to-utf-8-file-in-python
                    text_u_stop = tokenize_remove_stopwords_stem(text)
                    F.write(text_u_stop)
            except:  # OSError
                print('Writing file failed')
        else:
            print "denne har ikke kategori, dette har enda ikke skjedd"
            has_no_main_cat+=1
            #sys.exit(0)







# start.


# a function to creat frec frequencies dict
def add_data2dict(doc):
    try:
        htree = etree.ElementTree(html.document_fromstring(doc.encode('utf-8')))
    except:
        global failed_docs
        failed_docs+=1
        print "doc failed to be read, now total: %s. file: %s. Teller: %s" % (failed_docs, filename, doc_teller)
        return
    if (htree.xpath(".//attribute[@name='class1']/@value")):
        global doc_teller
        doc_teller+=1
        keyword_list = htree.xpath(".//attribute[@name='class1']/@value")[0].split(",")#.replace(',', '_')
        for w in keyword_list:
            cnt[w.strip().lower()] += 1

# first create a dict with frequencies for all keywords in use

# if I cannot load pickeld counter object (a json file, from previous runs)

if (os.path.isfile("freq_dist_keywords.json") and os.stat("freq_dist_keywords.json").st_size !=0):
    with open('freq_dist_keywords.json') as f:
        print "laster json: freq_dist_keywords"
        cnt = json.load(f)
else:
    print "lager freq_dist_keywords.json"
    from collections import Counter
    cnt = Counter()

    for root, subdirs, files in os.walk(walk_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            if not filename.endswith('.xml'): # skip .DStore
                continue # meaning skipping this iteration
            doc_teller+=1
            encodings = ['utf-8', 'iso-8859-1'] # ,'windows-1250', 'windows-1252'
            for e in encodings:
                try:
                    fh = codecs.open(file_path, 'r', encoding=e)
                    fh.readlines()
                    fh.seek(0)
                except UnicodeDecodeError:
                    print('\t- got unicode error with %s , trying different encoding' % e)
                else:
                    add_data2dict(fh.read())
                    if (doc_teller % 25000) == 0:
                        print doc_teller,
                    break
    with open('freq_dist_keywords.json', 'w') as f:
        json.dump(cnt, f)


print "dette er cnt objektet"
print cnt

#reset counters used
failed_docs = 0
has_category = 0
doc_teller = 0

print('walk_dir = ' + walk_dir)

# If your current working directory may change during script execution, it's recommended to
# immediately convert program arguments to an absolute path. Then the variable root below will
# be an absolute path as well. Example:
# walk_dir = os.path.abspath(walk_dir)
print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

for root, subdirs, files in os.walk(walk_dir):
    print('--\nroot = ' + root)

    for subdir in subdirs: # print out subfolders
        print('\t- subdirectory ' + subdir)

    for filename in files: # itterate over files
        file_path = os.path.join(root, filename)

        if not filename.endswith('.xml'): # skip .DStore
            continue # meaning skipping this iteration

        doc_teller+=1

        encodings = ['utf-8', 'iso-8859-1'] # ,'windows-1250', 'windows-1252'
        for e in encodings:
            try:
                fh = codecs.open(file_path, 'r', encoding=e)
                fh.readlines()
                fh.seek(0)
            except UnicodeDecodeError:
                print('\t- got unicode error with %s , trying different encoding' % e)
            else:
                # read this file, find the right category for it, and store in right folder
                #print('\t- (%s) opening the file %s with encoding:  %s ' % (doc_teller,file_path,e))
                find_text_and_subjects(fh.read())
                break #continue



print "doc_teller: %s" % (doc_teller)
print "failed_docs: %s" % (failed_docs)
print "has no main news cat: %s" % (has_no_main_cat)
print "has_category: %s" % (has_category)
print "estimated_nr_of_result_docs: %s" % (estimated_nr_of_result_docs)
print 'It took', time.time()-start, 'seconds.'
print "Length of ntb_id_list: %s" % (len(ntb_id_list))
