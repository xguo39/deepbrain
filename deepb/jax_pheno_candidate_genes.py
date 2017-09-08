import re
import pandas as pd
import pickle

all_phenos = []
gene_key_phenos = dict()
pheno_to_gene = dict()
with open('data/jax.txt', 'rb') as f:
    f.readline()
    for line in f:
        parts = line.split('\t') 
        gene, key_phenos = parts[1].upper(), parts[3]
        if gene == 'UNKNOWN' or not gene:
            continue
        key_phenos_ = re.sub(' +', ' ', key_phenos)
        key_phenos_ = key_phenos_.replace('/ ', '/')
        gene_key_phenos[gene] = key_phenos_
        phenos = re.split(r',|/|;', key_phenos)
        tmp_phenos = []
        for pheno in phenos:
            pheno = pheno.strip()
            pheno = pheno.lower() 
            pheno = re.sub(' +', ' ', pheno)
            if not pheno:
                continue
            if 'and ' in pheno:
                pheno = pheno.lstrip('and ')
            tmp_phenos.append(pheno)
            if pheno in pheno_to_gene:
                pheno_to_gene[pheno].append(gene)
            else:
                pheno_to_gene[pheno] = [gene]
        phenos = tmp_phenos
        all_phenos += phenos
all_phenos = list(set(all_phenos))
df_all_phenos = pd.Series(all_phenos)
df_all_phenos.sort_values(inplace = True) 
#df_all_phenos.to_csv('jaxphenos.txt', index = False)

print gene_key_phenos

print pheno_to_gene

associated_genes = dict()
with open('data/JAX_map_to_hpo.csv', 'rb') as f:
    f.readline()
    for line in f:
        line = line.strip()
        parts = line.split(',')
        jax_pheno = parts[0]
        hpo_ids = [parts[2].replace('_', ':')] 
        try:
            hpo_ids.append(parts[4].replace('_', ':'))
        except:
            pass
        try:
            hpo_ids.append(parts[6].replace('_', ':'))
        except:
            pass
        for hpo_id in hpo_ids:
            if hpo_id:
                if hpo_id in associated_genes:
                    if jax_pheno in pheno_to_gene:
                        associated_genes[hpo_id] += pheno_to_gene[jax_pheno]
                else: 
                    if jax_pheno in pheno_to_gene:
                        associated_genes[hpo_id] = pheno_to_gene[jax_pheno]

print associated_genes

outfile = open('data/jax_phenotypes.p', 'wb')
data = (associated_genes, gene_key_phenos)
pickle.dump(data, outfile)
outfile.close()

# Read pickle variables
#infile = open('data/jax_phenotypes.p', 'rb')
#associated_genes, gene_key_phenos = pickle.load(infile)
#infile.close()

'''
gene_key_phenos = {'KITL': 'coat color and belly spot', 'HPS5': 'coat color', 'HPS6': 'coat
color', 'HPS3': 'coat color', 'DAB1': 'neurological/behavioral: abnormal motor
capabilities/coordination/movement/balance/physical strength', ...}

pheno_to_gene = {'urinary': ['SPNA1', 'TMEM67  (AMONG OTHER GENES)'], 'head toss': ['LMX1A'],
'skeleton': ['DLL3', 'DSCAM', 'FBN2', 'FREM2', 'LRP4', 'PHEX', 'POFUT1'], ...}

associated_genes = {'HP:0002715': ['ABCG5', 'RELB'], 'HP:0000365': ['ARSB', 'CLIC5', 'COL2A1',
'DUOX2', 'FGFR3', 'HMX1', 'HMX1', 'LHFPL5', 'NOX3', 'OTOF', 'PHEX', 'POU3F4',
'PRKRA', 'TSHR', 'CDH23', 'LMX1A', 'SOSTDC1'], ...}
'''
