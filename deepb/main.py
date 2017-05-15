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
from collections import Counter


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

def read_input_pheno_file(input_phenotype):
    if not input_phenotype:
        return '', ''
    text = StringIO(unicode(input_phenotype), newline=None)
    lines = text.readlines()
    lines = [line.strip() for line in lines]
    phenos = []
    for line in lines:
        if not line:
            continue
        phenos_each_line = re.split(r'  +|\t+|,|;|\.|\|', line.strip())
        phenos_each_line = [re.sub(r'^\W+|\W+$', '', s) for s in phenos_each_line]
        phenos_each_line = [s.lower() for s in phenos_each_line if s]
        phenos += phenos_each_line

    corner_cases = dict()
    for pheno in phenos:
        if re.search('development', pheno) and re.search('delay', pheno) and not re.search('growth', pheno):
            phenos.append('growth delay')
            corner_cases['growth delay'] = pheno.strip()
    for pheno in phenos:
        if re.search('growth', pheno) and re.search('delay', pheno) and not re.search('development', pheno):
            phenos.append('developmental delay')
            corner_cases['developmental delay'] = pheno.strip()
    return phenos, corner_cases

def read_input_gene_file(input_gene):
	candidate_vars = []
	input_gene = input_gene.split('\n')
	header = input_gene[0]
	sniffer = csv.Sniffer()
	dialect = sniffer.sniff(header)
	delimiter =  dialect.delimiter
	field_names = header.split(delimiter)
	chrom_idx, pos_idx, ref_idx, alt_idx, gene_idx = None, None, None, None, 0 

	for idx in xrange(len(field_names)):
		field = field_names[idx]
		if re.match(r'chrom', field, re.I): chrom_idx = idx
		if re.match(r'pos|start', field, re.I): pos_idx = idx
		if re.match(r'ref', field, re.I): ref_idx = idx
		if re.match(r'alt|allele 1', field, re.I): alt_idx = idx
		if re.match(r'gene (gene)|gene', field, re.I): gene_idx = idx

	input_gene_list = []
	CANDIDATE_GENES = []
	for line in input_gene[1:]:
		if not line:
			continue
		line = line.rstrip()
		parts = re.split(r'%s' % delimiter, line)
		input_gene_list.append(parts)
		gene = parts[gene_idx]
		CANDIDATE_GENES.append(gene)
		transcript, variant, variant_id = '', '', ''
		for part in parts:
			if re.search(r'_.*:c\.', part):
				transcript, variant = part.split(':')
			else:
				if re.search(r'c\.', part):
					variant = part
				if re.search(r'NM_', part, re.I):
					transcript = part.split(':')[0]
			if re.search(r'_.*:g\.', part):
				variant_id = 'chr' + part.split(':')[0].split('.')[-1] + part.split(':')[-1]
			if re.search(r'chr.*:g\.', part, re.I):
				variant_id = part
		if not variant_id and (chrom_idx and pos_idx and ref_idx and alt_idx):
			chrome, pos, ref, alt = parts[chrom_idx], parts[pos_idx], parts[ref_idx], parts[alt_idx]
			variant_id = format_hgvs(chrome, pos, ref, alt)
		candidate_vars.append((gene, variant, transcript, variant_id))

        # remove lines in the input file which has wrong number of fields
        field_nums = []
        for line in input_gene_list:
			field_nums.append(len(line))
        count = Counter(field_nums)
        correct_field_num = count.most_common()[0][0]
        correct_input_gene_list = []
        for line in input_gene_list:
			if len(line) == correct_field_num:
				correct_input_gene_list.append(line)
        df_genes = pd.DataFrame(correct_input_gene_list, columns = field_names)
        return candidate_vars, CANDIDATE_GENES, df_genes, field_names 

def map_phenotype2gene(CANDIDATE_GENES, phenos, corner_cases, candidate_vars):
	ranking_genes, ranking_disease = map_phenotype_to_gene.generate_score(phenos, CANDIDATE_GENES, corner_cases)
	# collect variant info
	hpo_filtered_genes = np.unique([i[0] for i in ranking_genes]).tolist()

	tmp_candidate_vars = []
	for var in candidate_vars:
		if var[0] in hpo_filtered_genes:
			tmp_candidate_vars.append(var)
	candidate_vars = tmp_candidate_vars
	return ranking_genes, candidate_vars

def master_function(raw_input_id):
	status_step = "generating candidate variants ..." 
	raw_input = Raw_input_table.objects.get(id=raw_input_id)
	input_gene = raw_input.raw_input_gene
	input_phenotype = raw_input.raw_input_phenotype

	# Read input pheno file and generate phenos and corner_cases 
	phenos, corner_cases = read_input_pheno_file(input_phenotype)


	# Read input gene file and generate candidate_vars. candidate_vars are (gene, variant, transcript, variant_id); CANDIDATE_GENES is a list of gene symbols; df_genes is a dataframe that keeps all the data that user uploaded; field_names are header of the input gene file 
	candidate_vars, CANDIDATE_GENES, df_genes, field_names = read_input_gene_file(input_gene)

	# map phenotype to gene; the candidate_vars was filtered: if it is a gene associated with phenos, then keep it.

	if phenos:
		raw_input.status = "Maping phenotypes to genes"
		raw_input.save()
		ranking_genes, candidate_vars = map_phenotype2gene(CANDIDATE_GENES, phenos, corner_cases, candidate_vars)
	else:
		ranking_genes = []
		for gene in CANDIDATE_GENES:
			ranking_genes.append((gene, 1.0, 1))

	# collect variant info
	raw_input.status = "Annotating variants using genomic databases"
	raw_input.save()
	mv = myvariant.MyVariantInfo()
	final_res, variants = collectVariantInfo.get_variants(candidate_vars)

	# pubmed
	raw_input.status = "Searching biomedical literatures"
	raw_input.save()
	df_pubmed = pubmed.queryPubmedDB(final_res)

	# ACMG
	raw_input.status = "Checking ACMG standard"
	raw_input.save()
	df_hpo_ranking_genes = pd.DataFrame(ranking_genes, columns=['gene', 'score', 'hits'])
	df_hpo_ranking_genes = df_hpo_ranking_genes[['gene', 'score']]
	ACMG_result, variant_ACMG_interpretation, variant_ACMG_interpret_chinese = ACMG.Get_ACMG_result(df_hpo_ranking_genes, variants, df_pubmed)

	# filter variant on phenotype

	if phenos:
		raw_input.status = "Filtering variants based on phenotypes"
		raw_input.save()
		df_final_res, variant_ACMG_interpretation, variant_ACMG_interpret_chinese = filterVariantOnPhenotype.generateOutput(variants, ACMG_result, phenos, variant_ACMG_interpretation, variant_ACMG_interpret_chinese)
	else:
	    df_final_res = ACMG_result

	return df_final_res, df_genes, phenos, field_names, variant_ACMG_interpretation, variant_ACMG_interpret_chinese

