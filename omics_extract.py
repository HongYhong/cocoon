import multiprocessing
from typing import Text
import xml.etree.ElementTree as ET
from pprint import pprint
#import requests, bs4
import re
import ast
import re
from multiprocessing import Pool
from multiprocessing.managers import BaseManager
from multiprocessing import Manager

class XmlHandler(object):
    def __init__(self,xmlfile_path):
        xmlfile = open(xmlfile_path,'rb')
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        self.root = root
        self.xmlfile = xmlfile

    def pmc_pattern_print(self,outfile_path):
        outfile = open(outfile_path,'w')
        for item in self.root.iter(tag = 'article'):
            itemstring = ET.tostring(item,encoding = 'utf-8')
            front = item.find('front')
            article_meta = front.find('article-meta')

            for article_id in article_meta.findall('article-id'):
                if article_id.attrib['pub-id-type'] == 'pmid':
                    outfile.write('{}\t{}{}'.format(article_id.text,itemstring,'\n'))
            #print(pmid,itemstring)
        outfile.close()

class TextHandler(object):
    def __init__(self,textfilepath):
        textfile = open(textfilepath,'r')
        self.textfile = textfile

    def extract_omics_lines(self,pattern_file_path,outfile_path):
        '''
        extract lines that match the omics patterns in the file.
        '''
        outfile = open(outfile_path,'a')
        articles = self.textfile.readlines()
        with open(pattern_file_path,'r') as pattern_file:
            patterns = pattern_file.readlines()
        for article in articles:
            pmid = article.split('\t')[0]
            article = ast.literal_eval(article.split('\t')[1]).decode('utf-8')
            lines = article.splitlines()
            for line in lines:
                for pattern in patterns:
                    pattern = re.sub(r"\[\[:digit:\]\]",r"[0-9]",pattern).strip('\n')
                    if re.search(pattern,line,re.IGNORECASE) is not None:
                        outfile.write("{}\t{}\n".format(pmid,line))
        outfile.close()


def extract_cancer_lines(textfile_path,pattern_file_path,outfile_path,index):
    '''
    extract lines that match the cancer synosyms  in the file
    '''
    outfile = open(outfile_path,'a')
    textfile = open(textfile_path,'r')
    articles = textfile.readlines()
    with open(pattern_file_path,'r') as pattern_file:
        patterns = pattern_file.readlines()
    # for pattern in patterns:
    #     print(pattern.strip('\n'))
    article = articles[index]
    print("processing article:{}".format(index))
    pmid = article.split('\t')[0]
    article = ast.literal_eval(article.split('\t')[1]).decode('utf-8')
    lines = article.splitlines()
    for line in lines:
        for pattern in patterns:
            pattern = pattern.strip('\n')
            if re.search(pattern,line,re.IGNORECASE) is not None:
                outfile.write("{}\t{}\n".format(pmid,line))
    
    outfile.close()




if __name__ == '__main__':
    # xmlhandler = XmlHandler('./pmc_result_for_organoid_full_20210226.xml')
    # #xmlhandler.pmc_pattern_print('./pmc_result_for_organoid_full_pattern1_20210226.xml')

    # texthandler = TextHandler('pmc_result_for_organoid_full_pattern1_20210226.xml')
    # texthandler.extract_omics_lines('omics_keywords.txt','pmc_result_for_organoid_full_pattern1_lines_20210226.xml')

    num_lines = sum(1 for line in open('pmc_result_for_organoid_full_pattern1_match_omics.txt'))
    pool = multiprocessing.Pool(8)
    for index in range(num_lines):
        pool.apply_async(extract_cancer_lines,args=('pmc_result_for_organoid_full_pattern1_match_omics.txt','all_cancer_type_synonym.txt','pmc_result_for_organoid_full_pattern1_match_omics_cancer.txt',index))
    print('Waiting for all subprocesses done...')
    pool.close()
    pool.join()
    print('All subprocesses done.')




