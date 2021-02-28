from Bio import Entrez

# author : yanhong hong

class Entrez_Fetcher():

    def __init__(self,email,sorttype,query_term,pathToSave,retmode,mindate,database,rettype,maxdate = 3000,retmax = 10000000):
        self.email = email
        self.sorttype = sorttype
        self.retmax = retmax
        self.mindate = mindate
        self.maxdate = maxdate
        self.query_term = query_term
        self.retmode = retmode
        self.pathToSave = pathToSave
        self.database = database
        self.rettype = rettype

    def search(self,):
        Entrez.email = self.email
        handle = Entrez.esearch(
                                sort=self.sorttype, 
                                retmax=self.retmax,
                                retmode=self.retmode,
                                mindate=self.mindate,
                                term=self.query_term,
                                db = self.database
                                )
        results = Entrez.read(handle,validate=False)
        return results

    def fetch_details(self,results):
        Entrez.email = self.email
        handle = Entrez.efetch(
                                db=database,
                                retmax=self.retmax,
                                rettype = self.rettype,
                                retmode=self.retmode,
                                id=results['IdList']
                                )
        details_results = handle.read()
        return details_results

    def save_result(self,details_results):
        try:
            details_results = details_results.decode('utf-8')
        except:
            pass
        with open(self.pathToSave,'w') as f:
            f.write(details_results)

    def get_pmc_details(self,):
        try:
            results = self.search()
            details_results = self.fetch_details(results)
            self.save_result(details_results)
            return 'success!'
        except Exception as e:
            return e

if __name__ == '__main__':
    # results = search('(organoid[Title] OR organoid[Abstract] OR organoid[Body - All Words]) AND (cancer[Title] OR cancer[Abstract] OR cancer[Body - All Words])AND ("2010"[Publication Date] : "3000"[Publication Date]) ')
    # query_term = '(organoid[Title] OR organoid[Abstract] OR organoid[Body - All Words]) AND (cancer[Title] OR cancer[Abstract] OR cancer[Body - All Words])AND ("2010"[Publication Date] : "3000"[Publication Date])'
    # email = '524664992@qq.com'
    # sort_type = 'relevance'
    # mindate='2010'
    # pathToSave = './pmc_result_for_organoid_20210225.xml'
    # retmode = 'xml'
    # database = 'pmc'
    # pmc_fetcher = Entrez_Fetcher(email,sort_type,query_term,pathToSave,retmode,mindate,database)
    
    # status = pmc_fetcher.get_pmc_details()
    
    query_term = '(organoid) AND (cancer) AND ("2010"[Publication Date] : "3000"[Publication Date])'
    email = '524664992@qq.com'
    sort_type = 'relevance'
    mindate='2010'
    pathToSave = './pubmed_result_for_organoid_20210225.txt'
    rettype = 'summary'
    retmode = 'text'
    database = 'pubmed'
    pubmed_fetcher = Entrez_Fetcher(email,sort_type,query_term,pathToSave,retmode,mindate,database,rettype)
    status = pubmed_fetcher.get_pmc_details()
    print(status)


    #parsed_json = json.loads(papers)
    #print(json.dumps(papers, indent=4, sort_keys=True))
    #print(papers)
    # for i, paper in enumerate(papers['PubmedArticle']):
    #     print("{}) {}".format(i+1, paper['MedlineCitation']['Article']['ArticleTitle']))

    #print(fetch_details(['123','455']))