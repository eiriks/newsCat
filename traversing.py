#!/usr/bin/python2.7
# coding: utf-8
import os
import sys

walk_dir = sys.argv[1]


from time import time
from lxml import html
from lxml import etree
from urllib import quote
import urllib2
from hashlib import sha1
def find_text_and_subjects(newsml_content,
                           subject_tags=('SubjectMatter', 'SubjectDetail'),
                           text_tags=('HeadLine',),
                           html_tags=('body.content',),
                           ntbiptcsequence=('NTBIPTCSequence',)):
    # First parse of the document as XML for the structured attributes
    xtree = etree.ElementTree(etree.fromstring(newsml_content))
    #print xtree
    text_items = [e.text.strip()
                  for tag in text_tags
                  for e in xtree.findall('//' + tag)]

    dummy = etree.fromstring(newsml_content)
    for child in dummy:
        print(child.tag)
        for cchild in child:
            print('\t'+cchild.tag, cchild.get("name"))

    print "nuff"*20
    for element in dummy.iter():
        print("%s - %s - %s - %s" % (element.tag, element.text, element.get("name"), element.get('content')))

    # for tag in ntbiptcsequence:# for e in xtree.findall('//'+tag):
    #     print tag
    #     for e in xtree.findall('//' + tag):
    #         print e

    # for a in e
    # for e in xtree:
    #     print e

    print "text_items", text_items
    subjects = [IPTC_SUBJECT_PREFIX + e.get('FormalName')
                for tag in subject_tags
                for e in xtree.findall('//' + tag)]
    print "subjects", subjects
    # Then use HTML parser to find the that looks like HTML hence can leverage
    # the text_content method.
    htree = etree.ElementTree(html.document_fromstring(newsml_content))
 
    text_items += [e.text_content().strip()
                   for tag in html_tags
                   for e in htree.findall('//' + tag)]
    text = "\n\n".join(text_items)
    
    #return text, subjects


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

    #real_files = (filename for filename in files if filename not in ['.DS_Store']) #(airport for airport in airports if airport.is_important)
    #print real_files
    for filename in files:
    #for filename in real_files:
        file_path = os.path.join(root, filename)

        #print('\t- file %s (full path: %s)' % (filename, file_path))
        print('\t- %s' % (filename))
        # if filename not in ['.DS_Store']:
        #     print "do stuff with" + filename
        # with open(file_path, 'rb') as f:
        #     f_content = f.read()
        #     list_file.write(('The file %s contains:\n' % filename).encode('utf-8'))
        #     list_file.write(f_content)
        #     list_file.write(b'\n')

        # 1. now I first just want to find the elements of the NTB files

        if not filename.endswith('.xml'):
            continue # meaning skipping this iteration 

        newsml_content = open(file_path, 'rb').read()

        find_text_and_subjects(newsml_content)

        # 2. then store them in folders acording to cateories.

