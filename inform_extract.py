import multiprocessing
from os import close
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

    def pubmed_pattern_print(self,outfile_path):
        outfile = open(outfile_path,'w')
        for item in self.root.iter(tag = 'PubmedArticle'):
            articletitlestring = ET.tostring(item.find('MedlineCitation').find('Article').find('ArticleTitle'),encoding = 'utf-8',method = 'text').decode('utf-8').replace('\n','')
            # articletitlestring = re.sub('<[^<]+>','',articletitlestring)
            try:
                articleabstract = ET.tostring(item.find('MedlineCitation').find('Article').find('Abstract'),encoding = 'utf-8',method = 'text').decode('utf-8').replace('\n','').strip()
            except:
                articleabstract = ''

            pmid = ET.tostring(item.find('MedlineCitation').find('PMID'),encoding = 'utf-8' ,method = 'text').decode('utf-8').replace('\n','')

            try:
                databanklist = ET.tostring(item.find('MedlineCitation').find('Article').find('DataBankList'),encoding = 'utf-8' ,method = 'text').decode('utf-8').replace('\n','').strip()
            except:
                databanklist = ''

            outfile.write('{}\t{}\t{}\t{}\n'.format(pmid,articletitlestring,articleabstract,databanklist))

        outfile.close()


class TextHandler(object):
    def __init__(self,textfilepath):
        textfile = open(textfilepath,'r')
        self.textfile = textfile

    def pmc_extract_omics_lines(self,pattern_file_path,outfile_path):
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

    def pmc_extract_omics_terms(self,pattern_file_path,outfile_path):
        '''
        use the output of the last function as the input of this function.
        extract omics terms that match the omics patterns in the file.
        '''
        matchomics = []
        outfile = open(outfile_path,'w')
        lines = self.textfile.readlines()
        with open(pattern_file_path,'r') as pattern_file:
            patterns = pattern_file.readlines()
        for line in lines:
            pmid = line.split('\t')[0]
            for pattern in patterns:
                pattern = re.sub(r"\[\[:digit:\]\]",r"[0-9]",pattern).strip('\n')
                for matchomic in re.findall(pattern,line,re.IGNORECASE):
                    matchomics.append(matchomic)

            outfile.write('{}\t{}\n'.format(pmid,matchomics))
            matchomics = []
        
        outfile.close()



    def pmc_omics_terms_merge(self,outfile_path):
        '''
        remove redundancy of  recodes in pmc_result_for_organoid_full_pattern1_matchlines_omicsterms_v2.txt.
        '''
        outfile = open(outfile_path,'w')
        omics_terms_set = set()
        textfile = self.textfile
        lines = textfile.readlines()
        lastpmid = ''
        for line in lines:
            pmid = line.split('\t')[0]
            omics_terms_list = ast.literal_eval(line.split('\t')[1].strip('\n'))
            if pmid == lastpmid:
                for omics_term in omics_terms_list:
                    omics_terms_set.add(omics_term)
            else:
                outfile.write("{}\t{}\n".format(lastpmid,list(omics_terms_set)))
                lastpmid = pmid
                omics_terms_set.clear()
                for omics_term in omics_terms_list:
                    omics_terms_set.add(omics_term)

        outfile.write("{}\t{}\n".format(lastpmid,list(omics_terms_set)))
        outfile.close()

    def pmc_cancerterms_sort_merge(self,outfile_path):
        '''
        remove redundancy of  recodes in pmc_result_for_organoid_full_pattern1_match_omics_cancer_v2_cancerterms.txt.
        '''
        try:
            outfile = open(outfile_path,'w')
        except:
            print("something went wrone while reading the files.")
            exit(-1)
        try:
            lines = self.textfile.readlines()
            lines.sort()
            lines = list(set(lines))
            lines.sort()
            cancer_terms_set = set()
            lastpmid = ''
            for line in lines:
                pmid = line.split('\t')[0]
                cancerterms_list = ast.literal_eval(line.split('\t')[1].strip('\n'))
                if pmid == lastpmid:
                    for cancerterm in cancerterms_list:
                        cancer_terms_set.add(cancerterm)

                else:
                    outfile.write("{}\t{}\n".format(lastpmid,list(cancer_terms_set)))
                    lastpmid = pmid
                    cancer_terms_set.clear()
                    for cancerterm in cancerterms_list:
                        cancer_terms_set.add(cancerterm)
            
            outfile.write("{}\t{}\n".format(lastpmid,list(cancer_terms_set)))

        finally:
            outfile.close()

    def pmc_extract_cancer_terms(self,patternfile_path,outfile_path):
        '''
        use the output of the function extract_cancer_lines to extract cancer terms.
        '''
        cancer_terms_set = set()
        lastpmid = ''
        index = 0
        try:
            textfile = self.textfile
            patternfile = open(patternfile_path,'r')
            outfile = open(outfile_path,'w')
        except:
            print("something went wrong while reading the files")
            exit(-1)
        
        try:
            patterns = patternfile.readlines()
            lines = textfile.readlines()
            for line in lines:
                index += 1
                print("processing line:{}".format(index))
                pmid = line.split('\t')[0]
                if pmid == lastpmid:
                    for pattern in patterns:
                        pattern = pattern.strip('\n')
                        if re.search(pattern,line,re.IGNORECASE) is not None:
                            cancer_terms_set.add(pattern)
                else:
                    outfile.write("{}\t{}\n".format(lastpmid,list(cancer_terms_set)))
                    lastpmid = pmid
                    cancer_terms_set.clear()
                    for pattern in patterns:
                        pattern = pattern.strip('\n')
                        if re.search(pattern,line,re.IGNORECASE) is not None:
                            cancer_terms_set.add(pattern)

            outfile.write("{}\t{}\n".format(lastpmid,list(cancer_terms_set)))
            
                        
        except:
            print("extract_cancer_terms went wrong!")
            exit(-1)
        finally:
            outfile.close()


    def pubmed_extract_omics_cancer_terms(self,omics_pattern_file_path,cancername_pattern_file_path,outfile_path):
        '''
        extract words that match the omics patterns in the file.
        '''
        outfile = open(outfile_path,'w')
        matchomics=[]
        matchcancers=[]
        articles = self.textfile.readlines()
        with open(omics_pattern_file_path,'r') as omics_pattern_file:
            omics_patterns = omics_pattern_file.readlines()
        with open(cancername_pattern_file_path,'r') as cancername_pattern_file:
            cancername_patterns = cancername_pattern_file.readlines()
        for article in articles:
            pmid = article.split('\t')[0]
            for omics_pattern in omics_patterns:
                omics_pattern = re.sub(r"\[\[:digit:\]\]",r"[0-9]",omics_pattern).strip('\n')
                for matchomic in  re.findall(omics_pattern,article,re.IGNORECASE):
                    matchomics.append(matchomic)

                    
            for cancername_pattern in cancername_patterns:
                cancername_pattern = cancername_pattern.strip('\n')
                if re.search(cancername_pattern,article,re.IGNORECASE) is not None:
                    matchcancers.append(cancername_pattern)
                
            outfile.write('{}\t{}\t{}\n'.format(pmid,matchomics,matchcancers))
            matchomics=[]
            matchcancers=[]
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
    # texthandler.pmc_extract_omics_lines('omics_keywords.txt','pmc_result_for_organoid_full_pattern1_matchlines_20210226.xml')

    # num_lines = sum(1 for line in open('pmc_result_for_organoid_full_pattern1_match_omics.txt'))
    # pool = multiprocessing.Pool(8)
    # for index in range(num_lines):
    #     pool.apply_async(extract_cancer_lines,args=('pmc_result_for_organoid_full_pattern1_match_omics.txt','all_cancer_type_synonym.txt','pmc_result_for_organoid_full_pattern1_match_omics_cancer.txt',index))
    # print('Waiting for all subprocesses done...')
    # pool.close()
    # pool.join()
    # print('All subprocesses done.')

    # xmlhandler = XmlHandler('pubmed_result_for_organoid_summary.xml')
    # xmlhandler.pubmed_pattern_print('pubmed_result_for_organoid_summary_pattern1.xml')

    # texthandler = TextHandler('pubmed_result_for_organoid_summary_pattern1_match_omics.xml')
    # texthandler.pubmed_extract_omics_cancer_terms('omics_keywords_v2.txt','all_cancer_type_synonym.txt','pubmed_result_for_organoid_summary_pattern1_match_omics_cancer.xml')

    # texthandler = TextHandler('pmc_result_for_organoid_full_pattern1_20210226.xml')
    # texthandler.pmc_extract_omics_lines('omics_keywords_v2.txt','pmc_result_for_organoid_full_pattern1_matchlines_v2.txt')

    # num_lines = sum(1 for line in open('pmc_result_for_organoid_full_pattern1_match_omics_v2.txt'))
    # pool = multiprocessing.Pool(10)
    # for index in range(num_lines):
    #     pool.apply_async(extract_cancer_lines,args=('pmc_result_for_organoid_full_pattern1_match_omics_v2.txt','all_cancer_type_synonym.txt','pmc_result_for_organoid_full_pattern1_match_omics_cancer_v2.txt',index))
    # print('Waiting for all subprocesses done...')
    # pool.close()
    # pool.join()
    # print('All subprocesses done.')

    # texthandler = TextHandler('pmc_result_for_organoid_full_pattern1_matchlines_v2.txt')
    # texthandler.pmc_extract_omics_terms('omics_keywords_v2.txt','pmc_result_for_organoid_full_pattern1_matchlines_omicsterms_v2.txt')

    # texthandler = TextHandler('pmc_result_for_organoid_full_pattern1_matchlines_omicsterms_v2_clean.txt')
    # texthandler.pmc_omics_terms_merge('pmc_result_for_organoid_full_pattern1_matchlines_omicsterms_v2_clean_merge.txt')

    # texthandler = TextHandler('pmc_result_for_organoid_full_pattern1_match_omics_cancer_v2.txt')
    # texthandler.pmc_extract_cancer_terms('all_cancer_type_synonym.txt','pmc_result_for_organoid_full_pattern1_match_omics_cancer_v2_cancerterms.txt')

    texthandler = TextHandler('pmc_result_for_organoid_full_pattern1_match_omics_cancer_v2_cancerterms.txt')
    texthandler.pmc_cancerterms_sort_merge('pmc_result_for_organoid_full_pattern1_match_omics_cancer_v2_cancerterms_merge.txt')






