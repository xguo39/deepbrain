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

def queryPubmedDBGenes(candidate_vars, df_genes, cursor, db):
  genes_in_var_query = pd.unique(df_genes['Gene'].values).tolist()
  candidate_genes = []
  for var in candidate_vars:
     gene, variant, protein = var
     candidate_genes.append(gene)
  genes_to_be_queried = list(set(candidate_genes) - set(genes_in_var_query)) 
  if not genes_to_be_queried:
    return pd.DataFrame()
  # query pubmed articles mentioning genes in genes_to_be_queried
  query = "select gene, pmid, title, journal, year, impact_factor from pubmed_var where "
  for gene in genes_to_be_queried:
     query += "gene='%s' or " % (gene)
  query = query[0:-4]
  #cursor = db.cursor()
  cursor.execute(query)
  data = cursor.fetchall()
  db.close()
  res = []

  gene_pubmed_count = dict() 
  for line in data:
    gene, pmid, title, journal, year, impact_factor = line
    if gene in gene_pubmed_count:
      gene_pubmed_count[gene] += 1
    else:
      gene_pubmed_count[gene] = 1 

  genes_to_be_kept = []
  for gene in gene_pubmed_count.keys():
    if gene_pubmed_count[gene] <= 10:
      genes_to_be_kept.append(gene)
  #print len(genes_to_be_kept)
  for line in data: 
    gene, pmid, title, journal, year, impact_factor = line
    if gene in genes_to_be_kept:
      res.append([gene, pmid, title, journal, year, impact_factor])
  #print len(res)
  df = pd.DataFrame(res, columns = ['Gene', 'PMID', 'Title', 'Journal', 'Year', 'Impact_Factor'])
  df = df[['Gene', 'Title', 'Journal', 'Year', 'Impact_Factor', 'PMID']]
  df.drop_duplicates(inplace = True)
  return df

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
  df_pubmed_genes_novariant = queryPubmedDBGenes(candidate_vars, df, cursor, db)
  return df, df_pubmed_genes_novariant

