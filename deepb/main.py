import map_phenotype_to_gene
import collectVariantInfo
import pubmed
import ACMG
import filterVariantOnPhenotype
import csv

import pandas as pd
import numpy as np
import re
import myvariant
from deepb.models import Main_table, Raw_input_table
from io import StringIO

# input_phenotype = 'data/sample_patient_phenotype.txt'
# input_genes = 'data/sample_genes.txt'

def format_hgvs(chrom, pos, ref, alt):
    '''get a valid hgvs name from VCF-style "chrom, pos, ref, alt" data.

    Example:

        >>> myvariant.format_hgvs("1", 35366, "C", "T")
        >>> myvariant.format_hgvs("2", 17142, "G", "GA")
        >>> myvariant.format_hgvs("MT", 8270, "CACCCCCTCT", "C")
        >>> myvariant.format_hgvs("X", 107930849, "GGA", "C")

    '''
    chrom = str(chrom)
    if chrom.lower().startswith('chr'):
        # trim off leading "chr" if any
        chrom = chrom[3:]
    if len(ref) == len(alt) == 1:
        # this is a SNP
        hgvs = 'chr{0}:g.{1}{2}>{3}'.format(chrom, pos, ref, alt)
    elif len(ref) > 1 and len(alt) == 1:
        # this is a deletion:
        if ref[0] == alt:
            start = int(pos) + 1
            end = int(pos) + len(ref) - 1
            hgvs = 'chr{0}:g.{1}_{2}del'.format(chrom, start, end)
        else:
            end = int(pos) + len(ref) - 1
            hgvs = 'chr{0}:g.{1}_{2}delins{3}'.format(chrom, pos, end, alt)
    elif len(ref) == 1 and len(alt) > 1:
        # this is a insertion
        if alt[0] == ref:
            hgvs = 'chr{0}:g.{1}_{2}ins'.format(chrom, pos, int(pos) + 1)
            ins_seq = alt[1:]
            hgvs += ins_seq
        else:
            hgvs = 'chr{0}:g.{1}delins{2}'.format(chrom, pos, alt)
    elif len(ref) > 1 and len(alt) > 1:
        end = int(pos) + len(alt) - 1
        hgvs = 'chr{0}:g.{1}_{2}delins{3}'.format(chrom, pos, end, alt)
    else:
        raise ValueError("Cannot convert {} into HGVS id.".format((chrom, pos, ref, alt)))
    return hgvs

def master_function(raw_input_id):
	raw_input = Raw_input_table.objects.get(id=raw_input_id)
	input_gene = raw_input.raw_input_gene
	input_phenotype = raw_input.raw_input_phenotype

	# input_gene_list = [i.split('\t') for i in input_gene.split('\n')]
	# df_genes = pd.DataFrame(input_gene_list[1:-1], columns=input_gene_list[0])
	df_genes = pd.read_csv(StringIO(input_gene), sep = '\t')
	CANDIDATE_GENES = pd.unique(df_genes.Gene.values).tolist()

	corner_cases = dict()
	phenos = []
	input_phenotype = input_phenotype.split('\n')
	for line in input_phenotype:
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
	input_gene = input_gene.split('\n')
	header = input_gene[0]
	sniffer = csv.Sniffer()
	dialect = sniffer.sniff(header)
	delimiter =  dialect.delimiter
	field_names = header.split(delimiter)
	chrom_idx, pos_idx, ref_idx, alt_idx, gene_idx = None, None, None, None, None

	for idx in xrange(len(field_names)):
	    field = field_names[idx]
	    if re.match(r'chrom', field, re.I): chrom_idx = idx
	    if re.match(r'pos|start', field, re.I): pos_idx = idx
	    if re.match(r'ref', field, re.I): ref_idx = idx
	    if re.match(r'alt|allele 1', field, re.I): alt_idx = idx
	    if re.match(r'gene (gene)|gene', field, re.I): gene_idx = idx

	for line in input_gene:
	    line = line.rstrip()
	    parts = line.split(delimiter)
	    if gene_idx:
	        gene = parts[gene_idx]
	    else:
	        gene = parts[0]
	    if gene not in hpo_filtered_genes:
	        continue
	    transcript, variant, variant_id = '', '', ''
	    for part in parts:
	        if re.search(r'_.*:c\.', part):
	            transcript, variant = part.split(':')
	        if re.search(r'_.*:g\.', part):
	            variant_id = 'chr' + part.split(':')[0].split('.')[-1] + part.split(':')[-1]
	        if re.search(r'chr.*:g\.', part, re.I):
	            variant_id = part
	    if not variant_id and (chrom_idx and pos_idx and ref_idx and alt_idx):
	        chrome, pos, ref, alt = parts[chrom_idx], parts[pos_idx], parts[ref_idx], parts[alt_idx]
	        variant_id = format_hgvs(chrome, pos, ref, alt)
	    candidate_vars.append((gene, variant, transcript, variant_id))

	final_res, variants = collectVariantInfo.get_variants(candidate_vars)

	# pubmed
	df_pubmed = pubmed.queryPubmedDB(final_res)

	# ACMG
	df_hpo_ranking_genes = pd.DataFrame(ranking_genes, columns=['gene', 'score', 'hits'])
	df_hpo_ranking_genes = df_hpo_ranking_genes[['gene', 'score']]
	ACMG_result = ACMG.Get_ACMG_result(df_hpo_ranking_genes, variants, df_pubmed)

	# filter variant on phenotype
	df_final_res = filterVariantOnPhenotype.generateOutput(variants, ACMG_result, phenos)


	return df_final_res, df_genes, phenos

