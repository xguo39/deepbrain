import pandas as pd
import time
import sys
import MySQLdb
import os.path
BASE = os.path.dirname(os.path.abspath(__file__))

reload(sys)
sys.setdefaultencoding('utf-8')
pd.options.display.max_colwidth = 10000

# start_program = time.time()

# VARIANT_INFO_FILE = 'result/variants.txt'

db = MySQLdb.connect(host="localhost",    
                     user="root",       
                     passwd="Tianqi12", 
                     db="Aivar")       

# def readCandidateVarFile():
#     candidate_vars = []
#     with open(VARIANT_INFO_FILE, 'rb') as f:
#         f.readline()
#         for line in f.readlines():
#         line = line.rstrip()
#         parts = line.split('\t')
#             gene, variant, protein = parts[0], parts[1], parts[2]
#             candidate_vars.append((gene, variant, protein))
#     return candidate_vars 

def queryPubmedDB(candidate_vars):
   genevar2protein, geneprotein2var = {}, {}
   query = "select gene, protein_variant, pmid, title, journal, year, impact_factor, abstract from pubmed_var where "
   for var in candidate_vars:
       gene, variant, protein = var
       genevar2protein[(gene, variant)] = protein
       geneprotein2var[(gene, protein)] = variant 
       query += "(gene='%s' and lower(protein_variant)='%s') or (gene='%s' and lower(protein_variant)='%s') or " % (gene, variant.lower(), gene, protein.lower())
   query = query[0:-4]
   cursor = db.cursor()
   cursor.execute(query)
   data = cursor.fetchall()
   res = []
   for line in data:
       gene, protein_variant, pmid, title, journal, year, impact_factor, abstract = line 
       if protein_variant.startswith('p.'):
           variant, protein = geneprotein2var[(gene, protein_variant)], protein_variant
       else:
           variant, protein = protein_variant, genevar2protein[(gene, protein_variant)]
       res.append([gene, variant, protein, pmid, title, journal, year, impact_factor, abstract])
   db.close() 

   df = pd.DataFrame(res, columns = ['Gene', 'Variant', 'Protein', 'PMID', 'Title', 'Journal', 'Year', 'Impact_Factor', 'Abstract'])
   df = df[['Gene', 'Variant', 'Protein', 'Title', 'Journal', 'Year', 'Impact_Factor', 'Abstract', 'PMID']]
   df.drop_duplicates(inplace = True)
   df = df[df.Abstract.notnull() & (df.Abstract != '')]
   # return df
   # candidate_vars = readCandidateVarFile()
   #  df = queryPubmedDB(candidate_vars)
   df.to_csv(os.path.join(BASE, 'result/pubmed_query_results.csv'), index = False, sep = '\t')


   