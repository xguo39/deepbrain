import pandas as pd
import time
import sys
import MySQLdb
import amino_acid_mapping
import re
import os.path
BASE = os.path.dirname(os.path.abspath(__file__))

reload(sys)
sys.setdefaultencoding('utf-8')
pd.options.display.max_colwidth = 10000

# start_program = time.time()

# VARIANT_INFO_FILE = 'result/variants.txt'  

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

def convertAminoAcidLowertoCap1letter(protein):
  global robj_amino_acid
  protein = protein.lower()
  protein = robj_amino_acid.sub(lambda m: amino_acid_mapping.mapl2u[m.group(0)], protein)
  return protein

def queryPubmedDB(candidate_vars):
  db = MySQLdb.connect(host="127.0.0.1",    
                     user="root",       
                     passwd="Tianqi12", 
                     db="DB_offline")
  genevar2protein, geneprotein2var = {}, {}
  query = "select gene, protein_variant, pmid, title, journal, year, impact_factor, abstract, pathogenicity_score from pubmed_var where "
  for var in candidate_vars:
     gene, variant, protein = var
     genevar2protein[(gene, variant)] = protein
     geneprotein2var[(gene, protein)] = variant 
     query += "(gene='%s' and lower(protein_variant)='%s') or (gene='%s' and lower(protein_variant)='%s') or " % (gene, variant.lower(), gene, protein.lower())
  query = query[0:-4]
  cursor = db.cursor()
  cursor.execute(query)
  data = cursor.fetchall()
  db.close()
  res = []
  
  # print 'candidate_vars', candidate_vars
  # print 'genevar2protein', genevar2protein

  global robj_amino_acid
  robj_amino_acid = re.compile('|'.join(amino_acid_mapping.mapl2u.keys()))  

  for line in data:
    gene, protein_variant, pmid, title, journal, year, impact_factor, abstract, pathogenicity_score = line 
    if protein_variant.startswith('p.'):
      protein_variant = convertAminoAcidLowertoCap1letter(protein_variant) 
      variant, protein = geneprotein2var[(gene, protein_variant)], protein_variant
    else:
      variant, protein = protein_variant, genevar2protein[(gene, protein_variant)]
    res.append([gene, variant, protein, pmid, title, journal, year, impact_factor, abstract, pathogenicity_score])
  df = pd.DataFrame(res, columns = ['Gene', 'Variant', 'Protein', 'PMID', 'Title', 'Journal', 'Year', 'Impact_Factor', 'Abstract', 'pathogenicity_score'])
  df = df[['Gene', 'Variant', 'Protein', 'Title', 'Journal', 'Year', 'Impact_Factor', 'Abstract', 'PMID', 'pathogenicity_score']]
  df.drop_duplicates(inplace = True)
  df = df[df.Abstract.notnull() & (df.Abstract != '')]
  return df


