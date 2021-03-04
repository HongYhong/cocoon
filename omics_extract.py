import xml.etree.ElementTree as ET
from pprint import pprint
import requests, bs4
import re

class XmlHandler():
    def __init__(self,xmlfile_path):
        tree = ET.parse(xmlfile_path)
        root = tree.getroot()
        self.root = root

    def pattern_print(self,):
        outfile = open('./pmc_result_for_organoid_full_pattern1_20210226.xml','w')
        for item in self.root.iter(tag = 'article'):
            itemstring = ET.tostring(item,encoding = 'utf-8')
            front = item.find('front')
            article_meta = front.find('article-meta')

            for article_id in article_meta.findall('article-id'):
                if article_id.attrib['pub-id-type'] == 'pmid':
                    outfile.write('{}\t{}{}'.format(article_id.text,itemstring,'\n'))
            #print(pmid,itemstring)
        outfile.close()


if __name__ == '__main__':
    xmlhandler = XmlHandler('./pmc_result_for_organoid_full_20210226.xml')
    xmlhandler.pattern_print()
