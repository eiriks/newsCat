#!/usr/bin/python2.7
# coding: utf-8

import os, sys
import pymysql
import codecs
from preprocessor import make_parser    # https://github.com/peter17/mediawiki-parser
from text import make_parser

def write_to_file(with_name, write_this, folder="nn_wiki"):
    with_name = str(with_name)

    if not os.path.exists('./data'):            # create data folder if not exists
        os.makedirs('./data')
    if not os.path.exists('./data/'+folder+'/'):     # create data/sport folder is not exist
        os.makedirs('./data/'+folder+'/')

    # with open(os.path.join('./data/sport/',with_name), "w") as F:
    try:
        with codecs.open(os.path.join('./data/'+folder+'/',with_name), "w", "utf-8-sig") as F:  # http://stackoverflow.com/questions/934160/write-to-utf-8-file-in-python
            F.write(write_this)
    except:  # OSError
        print('Well darn.')

conn = pymysql.connect(
                    unix_socket="/Applications/MAMP/tmp/mysql/mysql.sock",
                     user="****", # your username
                      passwd="****", # your password
                      db="****",# name of the database
                      charset = "utf8", # encoding
                      use_unicode = True) 

cur = conn.cursor()
cur.execute("USE nrk;")

sql = """SELECT * FROM text WHERE old_id ='2270624' """

cur.execute(sql)

for row in cur.fetchall():
    d_title = row[0]
    templates = {}
    preprocessor = make_parser(templates)
    parser = make_parser()
    d_text = row[1]
    preprocessed_text = preprocessor.parse(d_text)
    output = parser.parse(preprocessed_text.leaves())
    
    d_text = output
    
    print output
    #write_to_file(d_title,d_text,folder="nn_wiki""") # .encode('utf8')

cur.close()