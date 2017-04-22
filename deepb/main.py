import map_phenotype_to_gene
import collectVariantInfo
import pubmed
import ACMG

import pandas as pd
import numpy as np
import re
import myvariant

# input_phenotype = 'data/sample_patient_phenotype.txt'
# input_genes = 'data/sample_genes.txt'

def master_function(input_phenotype,input_genes):
	#input 


	df_genes = pd.read_csv(input_genes, sep = '\t', usecols = [0])
	CANDIDATE_GENES = pd.unique(df_genes.Gene.values).tolist()

	corner_cases = dict()
	with open(input_phenotype, 'rb') as infile:
	    phenos = []
	    for line in infile:
	        if line.startswith('#') or not line.strip():
	            continue
	        line = line.rstrip()
	        phenos += line.split(',')
	        for pheno in phenos:
	            if re.search('development', pheno) and re.search('delay', pheno) and not re.search('growth', pheno):
	                phenos.append('growth delay')
	                corner_cases['growth delay'] = pheno.strip()
	        for pheno in phenos:
	            if re.search('growth', pheno) and re.search('delay', pheno) and not re.search('development', pheno):
	                phenos.append('developmental delay')
	                corner_cases['developmental delay'] = pheno.strip()
	    phenos = [_.strip() for _ in phenos]


	# map phenotype to gene
	mv = myvariant.MyVariantInfo()

	ranking_genes, ranking_disease = map_phenotype_to_gene.generate_score(phenos, CANDIDATE_GENES, corner_cases)


	# collect variant info
	hpo_filtered_genes = np.unique([i[0] for i in ranking_genes]).tolist()

	candidate_vars = []
	with open(input_genes, 'rb') as f:
		f.readline()
		for line in f.readlines():
			line = line.rstrip()
			parts = line.split('\t')
			gene = parts[0]
			if gene not in hpo_filtered_genes:
				continue
			for part in parts:
				if re.search(r'_.*:', part):
			  		transcript, variant = part.split(':') 
			candidate_vars.append((gene, variant, transcript))

	final_res, variants = collectVariantInfo.get_variants(candidate_vars)

	# pubmed
	# pubmed.queryPubmedDB(final_res)

	# ACMG
	df_hpo_ranking_genes = pd.DataFrame(ranking_genes, columns=['gene','score','hits'])
	df_hpo_ranking_genes = df_hpo_ranking_genes[['gene','score']]
	ACMG_result = ACMG.Get_ACMG_result(df_hpo_ranking_genes, variants)

	return ACMG_result, df_genes, phenos




