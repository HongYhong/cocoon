# COCOON

` author : yanhong hong`

**COCOON**(**CO**lle**C**ti**O**ns of **O**rga**N**oid) or **CORGIDB** (**C**omprehensive **ORG**ano**I**d **D**ata**B**ase)

<img src="./cocoon-logo.png" alt="drawing" height="400"/>

(1)Query1 used to search the **pmc** database:

```sql
((organoid) AND cancer) NOT (organoid[Reference]) AND ("2010"[Publication Date] : "3000"[Publication Date]) 
```

Search results:9680 items.

And we download the results as xml format: ` pmc_result_for_organoid_full_20210225.xml` .

download the summery as txt format:` pmc_result_for_organoid_summary_20210225.txt` .



(2)Query2 used to search the pmc database: (This query seems to be more reliable)

```sql
(organoid[Title] OR organoid[Abstract] OR organoid[Body - All Words]) AND (cancer[Title] OR cancer[Abstract] OR cancer[Body - All Words])AND ("2010"[Publication Date] : "3000"[Publication Date]) 
```

Search results:5623 items.

And we download the results as xml and txt formats:` pmc_result_for_organoid_full_20210226.xml` and ` ` ` pmc_result_for_organoid_summary_20210226.txt`



(3)Query used to search the pubmed database:

```sql
(organoid) AND (cancer) AND ("2010"[Publication Date] : "3000"[Publication Date]) 
```

Search results:2467 items.

And we download the results as xml format: `pubmed_result_for_organoid_full_20210225.xml ` .

download the summery as txt format: ` pubmed_result_for_organoid_summary_20210225.txt` .



What we want to extract?

(1) tumor type

(2) sample amount

(3) omics data type

(4) the accession number of the dataset

(5)...

(6)...



How to extract the above information:

(1) search for some key words for omics data.(e.g. sra, eda, gse , geo , data availability ...). result :we get a list of matched article titles.

expected results:

```txt
<article-title>	<omics-data link>
```



(2) We use a list of key words (**corpus**) about various cancer type to extract the tumor type information from abtsract and body text using the xml file format.

We extract key words from three sources:` extract_disease_oncology.py` .

(source 1) script1 used to extract tumor types key words from wiki.(https://en.wikipedia.org/wiki/List_of_cancer_types)

```python
from lxml import html
from urllib.request import ProxyHandler,build_opener

proxy = ProxyHandler({'https': 'https://hyh:hyh2102011@10.10.115.225:1080'})
opener = build_opener(proxy)
url = 'https://en.wikipedia.org/wiki/List_of_cancer_types'

html_text = opener.open(url).read().decode('utf-8')
tree = html.fromstring(html_text)
elements = tree.xpath('//*[@id="mw-content-text"]/div[1]/ul/li')

for element in elements:
    print ("".join(element.xpath('descendant-or-self::text()')))
```

Manual curated the outputs. > the result file is ` wiki_cancer_type.txt` .



(source 2)  script2 used to extract tumor types key words from cancer gov.(https://www.cancer.gov/types)

```python
import requests
from bs4 import BeautifulSoup

url = 'https://www.cancer.gov/types'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
mydivs = soup.find_all("ul", {"class": "cancer-list"})
alltext = [row.text for row in mydivs]
for text in alltext:
    print(text)
```

Manual curated the outputs. > the result file is ` cancer_type_cancergov.txt` . 



(source 3) (the data is from https://github.com/DiseaseOntology/HumanDiseaseOntology/blob/main/src/ontology/subsets/DO_cancer_slim.json)

script used to extract key words.

result : ` DO_cancer_slim.json`

```shell
cat cancer_type_cancergov.txt disease_oncology_lbl.txt disease_oncology_synonym.txt wiki_cancer_type.txt |sort|uniq > all_cancer_type_synonym.txt
```

We integrate three sources to one file: ` all_cancer_type_synonym.txt` .

Total key words number: 1562.



e.g. remove redundancy, remove unwanted key words.



cases we need to consider include:

(1) The omics data comes from the organoids involved in the article.(e.g. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6423033/ )

(2) The omics data comes from public data just for validation of the results.(e.g. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7565382/)



