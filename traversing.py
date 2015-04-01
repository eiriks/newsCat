#!/usr/bin/python2.7
# coding: utf-8
import os
import sys
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




# This file is a total mess, that takes a folder with NTB newsml-ish xml files as input
# extrakts the texts and stores them in a folder "ntb_data" acoring to category.
# Each file is stored once per category they are assigned with. 
# 


def isInt(val):
    return val == int(val)


# 5th of March 2015
# I keep running into problems 
# some files gives mw this: lxml.etree.XMLSyntaxError: Start tag expected, '<' not found, line 1, column 1
# but I dont get why - the files look perfectly fine.
# I'll try to skip them, and count how many there are.. 
failed_docs = 0
has_category = 0
estimated_nr_of_result_docs = 0
doc_teller = 0
ntb_id_list = []

def find_text_and_subjects(newsml_content,
                           subject_tags=('SubjectMatter', 'SubjectDetail'),
                           text_tags=('HeadLine', 'hedline'),
                           html_tags=('hedline', 'body.content', 'tagline'),
                           ntbiptcsequence=('NTBIPTCSequence',)):

    # First parse of the document as XML for the structured attributes
    try:
        xtree = etree.ElementTree(etree.fromstring(newsml_content.encode('utf-8')))
    except:
        global failed_docs
        failed_docs+=1
        print "doc failed to be read, not total: %s" % (failed_docs)
        return

    #print xtree
    
    # asuming this fail if xpath selector falls short. 
    if (xtree.findall(".//tobject.subject[@tobject.subject.refnum]")):
        global has_category
        has_category+=1
        # and add num of cats so I can know how many docs I get if 
        # I store one copy of the text pr category
        global estimated_nr_of_result_docs
        estimated_nr_of_result_docs+=len(xtree.findall(".//tobject.subject[@tobject.subject.refnum]"))

        # if we have dealt with this text before: skip it
        # beacause there are many redundant texts, I think I'd like to keep track of NTBIDs, to
        # keep redundancy to a minimum (hope NTBID is a true primary key)
        # <meta name="NTBID" content="RED140102_111408_al" />
        # ... it turs out not all docs had NTBID
        # will try <doc-id regsrc="NTB" id-string="FRX20140112T151237_nat" /> 
        #insted
        global ntb_id_list
        #this_docs_id = xtree.xpath(".//meta[@name='NTBID']/@content")
        this_docs_id = xtree.xpath(".//doc-id/@id-string")
        #print this_docs_id
        this_docs_id = unicode(this_docs_id[0])
        #print type(str(test[0])), str(test[0])
        # if we already have this, break out of this, just return, I presume
        if this_docs_id in ntb_id_list:
            return

        ntb_id_list.append(this_docs_id) # so I should get way fewer docs in ntb_data folders than org input


        text_items = [e.text.strip()
                      for tag in text_tags
                      for e in xtree.findall('//' + tag)]
        
        # Then use HTML parser to find the that looks like HTML hence can leverage
        # the text_content method.

        htree = etree.ElementTree(html.document_fromstring(newsml_content.encode('utf-8')))
     
        text_items += [e.text_content().strip()
                       for tag in html_tags 
                       for e in htree.findall('//' + tag)]
        text = "\n\n".join(text_items)
        #print "\t\t-->" +text[:100] + " [...]"



        # texts can have multiple categories so I store one copy of the text for each
        # cathegory, so that all relevant categories get the words (as in bag of words)
        # they deserve, according to NTB categorization
        for obj in xtree.findall(".//tobject.subject[@tobject.subject.refnum]"):
            #print etree.tostring(obj)
            #print obj.attrib['tobject.subject.refnum'], type(int(obj.attrib['tobject.subject.refnum'])), isInt(int(obj.attrib['tobject.subject.refnum']))
            if isInt( int(obj.attrib['tobject.subject.refnum']) ) :
                #print iptc_codes[obj.attrib['tobject.subject.refnum']], obj.attrib['tobject.subject.refnum']
                print "\t+ kategori: " + ",".join(iptc_codes[obj.attrib['tobject.subject.refnum']][:-1]) # obj.attrib['tobject.subject.refnum']
                
                main_cat = iptc_codes[obj.attrib['tobject.subject.refnum']][1]
                
                # now create folders
                if not os.path.exists('./ntb_data'):            # create data folder if not exists
                    os.makedirs('./ntb_data')
                if not os.path.exists('./ntb_data/'+main_cat+'/'):     # create data/sport folder is not exist
                    os.makedirs('./ntb_data/'+main_cat+'/')

                # now save this doc in the right folder.
                try:
                    with codecs.open(os.path.join('./ntb_data/'+main_cat+'/',filename), "w", "utf-8-sig") as F:  # http://stackoverflow.com/questions/934160/write-to-utf-8-file-in-python
                        F.write(text)
                except:  # OSError
                    print('Writing file failed')

            else:
                print "tobject.subject.refnum is not a number"
                return
    else:
        print "doc has no categories"

    # subjects = [IPTC_SUBJECT_PREFIX + e.get('FormalName')
    #             for tag in subject_tags
    #             for e in xtree.findall('//' + tag)]
    # for tag in html_tags:
    #     for e in xtree.findall('//' + tag):
    #         print e#.text_content().strip()
    # print "subjects", subjects

    #print "text_items", text_items
    # subjects = [IPTC_SUBJECT_PREFIX + e.get('FormalName')
    #             for tag in subject_tags
    #             for e in xtree.findall('//' + tag)]
    # print "subjects", subjects
 
    # return text, subjects




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
                print('\t- (%s) opening the file %s with encoding:  %s ' % (doc_teller,file_path,e))
                find_text_and_subjects(fh.read())
                break #continue  
        #newsml_content = open(file_path, 'rb').read()

        # 2. then store them in folders acording to cateories.
        # this is done in the find_text_and_subjects() function, this function 
        # should probably just be removed as linear code where it is run... 

print "doc_teller: %s" % (doc_teller)
print "failed_docs: %s" % (failed_docs)
print "has_category: %s" % (has_category)
print "estimated_nr_of_result_docs: %s" % (estimated_nr_of_result_docs)
print 'It took', time.time()-start, 'seconds.'
print "Length of ntb_id_list: %s" % (len(ntb_id_list))