# aivar

1. install tensorflow 0.12.1


2. run 'source activate tensorflow' and install:

A. install numpy 1.12.0

B. install pandas 0.19.2

C. install nltk 3.2.2

D. install myvariant 0.3.1

E. install mygene 3.0.0

F. pip install python-Levenshtein

G. pip install json2html

H. install BeautifulSoup 4.5.3

I. install pattern 2.6

J. Install gensim 0.13.4.1

H. pip install lxml

3. Download data.zip file from google drive: https://drive.google.com/open?id=0B0xy23UDXrIAcFJHTUVCSEdQSlU and unzipped to data/

The input files for the program are:

A. data/sample_patient_phenotype.txt

B. data/sample_genes.txt


4. Run the following commands in sequence to get final output: result/ACMG_variant_pathogenicity_result.txt

To begin with, you need to first active your container in order to run tensor flow (if you install tensor flow with virtual env)

A. python map_phenotype_to_gene.py

B. python collectVariantInfo.py

C. python pubmed.py

D. python ACMG.py


5. You may need to install nltk.corpus.wordnet and punkt by
   1) enter the python shell
   2) >>> import nltk
   3) >>> nltk.download()
   Then there will be an install window come out. Please select corpus tab and download the wordnet from the list. Also select the Model tab download punkt

