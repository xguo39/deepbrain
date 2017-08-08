# -*- coding: utf-8 -*-

import map_phenotype_to_gene
import collectVariantInfo
import pubmed
import ACMG
import filterVariantOnPhenotype
import update_phenotype_to_gene
import csv

import pandas as pd
import numpy as np
import re
import myvariant
from deepb.models import Main_table, Raw_input_table
from io import StringIO
from collections import Counter
from collections import defaultdict
from langdetect import detect
import urllib2
import json
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

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
    if chrom == '.' or pos == '.' or ref == '.' or alt == '.' or not chrom or not pos or not ref or not alt or ref == alt:
    	return ''
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
		return '', '', '', ''
	language = detect(unicode(input_phenotype))
	phenotype_translate = None
	if language == "zh-cn" or language == "ko":
		site = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-Hans&tl=en&dt=t&q="+input_phenotype
		hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
				'Accept-Encoding': 'none',
				'Accept-Language': 'en-US,en;q=0.8',
				'Connection': 'keep-alive'}
		req = urllib2.Request(site, headers=hdr)
		try:
			page = urllib2.urlopen(req)
			content = page.read()
			phenotype_translate = json.loads(content)[0][0][0]
			input_phenotype = phenotype_translate
		except urllib2.HTTPError, e:
			return '', '', '', ''
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
	original_phenos = [_.strip() for _ in phenos]
	for pheno in phenos:
		if re.search('development', pheno) and re.search('delay', pheno) and not re.search('growth', pheno):
			phenos.append('growth delay')
			corner_cases['growth delay'] = pheno.strip()
		for pheno in phenos:
			if re.search('growth', pheno) and re.search('delay', pheno) and not re.search('development', pheno):
				phenos.append('developmental delay')
				corner_cases['developmental delay'] = pheno.strip()
		phenos = [_.strip() for _ in phenos]
		phenos = list(set(phenos))
		return phenos, corner_cases, original_phenos, phenotype_translate

def getFileDelimiter(inputfile):
	for line in inputfile:
	    if line and line[:2] != "##":
	        header = line
	        sniffer = csv.Sniffer()
	        dialect = sniffer.sniff(header)
	        delimiter =  dialect.delimiter
	        field_names = header.split(delimiter)
	        break
    return delimiter, field_names

def convertFile2DF(inputfile, delimiter):
    columns = []
    vcf_data = []
    for line in inputfile[1:]:
        if not line:
            continue
        if line.startswith('#'):
            if not line.startswith('##'):
		        line = line.rstrip()
		        columns = re.split(r'%s' % delimiter, line)
                columns[0] = columns[0][1:]
            continue
		line = line.rstrip()
		parts = re.split(r'%s' % delimiter, line)
        vcf_data.append(parts)
    df_vcf_data = pd.DataFrame(vcf_data, columns = columns)
    return df_vcf_data

def read_input_gene_file(input_gene, parent_ngs, father_vcf, mother_vcf):
	candidate_vars = []
	input_gene = input_gene.split('\n')

    delimiter, field_names = getFileDelimiter(input_gene)
    if father_vcf or mother_vcf:
        df_vcf = convertFile2DF(input_gene, delimiter)

        df_vcf_father, df_vcf_mother = pd.DataFrame(), pd.DataFrame()
        if father_vcf:
            delimiter_f, field_names_f = getFileDelimiter(father_vcf)
            df_vcf_father = convertFile2DF(father_vcf, delimiter_f)
        if mother_vcf:
            delimiter_m, field_names_m = getFileDelimiter(mother_vcf)
            df_vcf_mother = convertFile2DF(mother_vcf, delimiter_m)

        if father_vcf:
            df_vcf = df_vcf.merge(df_vcf_father[['CHROM', 'POS', 'ALT']], how = 'left', on = ['CHROM', 'POS'])
        else:
            df_vcf['FATHER'] = ''
        if mother_vcf:
            df_vcf = df_vcf.merge(df_vcf_mother[['CHROM', 'POS', 'ALT']], how = 'left', on = ['CHROM', 'POS'])
        else:   
            df_vcf['MOTHER'] = ''
        df_vcf.columns = df_vcf.columns.values.tolist()[0:-2] + ['FATHER', 'MOTHER'] 
        field_names = df_vcf.columns.values.tolist()
        input_gene = df_vcf.values.tolist()       
        input_gene = ['dummy line'] + input_gene 
	
	chrom_idx, pos_idx, ref_idx, alt_idx, gene_idx, zygosity_idx = None, None, None, None, None, None
	mother_idx, father_idx = None, None

	for idx in xrange(len(field_names)):
	    field = field_names[idx]
	    if re.match(r'chrom|#chrom', field, re.I): chrom_idx = idx
	    if re.match(r'pos|start', field, re.I): pos_idx = idx
	    if re.match(r'ref', field, re.I): ref_idx = idx
	    if re.match(r'alt|allele 1', field, re.I): alt_idx = idx
	    if re.match(r'gene \(gene\)|gene$', field, re.I): gene_idx = idx
	    if re.match(r'zygo', field, re.I): zygosity_idx = idx
	    if re.match(r'mot', field, re.I): mother_idx = idx
	    if re.match(r'fat', field, re.I): father_idx = idx

	input_gene_list = []
	CANDIDATE_GENES = []
	candidate_vars_zygosity = []
	for line in input_gene[1:]:
		if not line:
			continue	
		if line.startswith("#"):
			continue
		line = line.rstrip()
		# print line
		parts = re.split(r'%s' % delimiter, line)
		input_gene_list.append(parts)
		gene, transcript, variant, variant_id, zygosity = '', '', '', '', ''
		if gene_idx is not None:
			gene = parts[gene_idx]
			CANDIDATE_GENES.append(gene)
		for part in parts:
			# print part
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
			if re.match(r'het|hom|hem|de |comp', part, re.I):	
				zygosity = part

		if not variant_id and (chrom_idx is not None and pos_idx is not None and ref_idx is not None and alt_idx is not None):
			chrome, pos, ref, alt = parts[chrom_idx], parts[pos_idx], parts[ref_idx], parts[alt_idx]
			alts = alt.split(',')
			for alt in alts:
				try:
					variant_id = format_hgvs(chrome, pos, ref, alt)
				except ValueError:
					pass
				# print gene, variant, transcript, variant_id
				if not gene and not variant and not transcript and not variant_id:
					continue
				if mother_idx is not None and father_idx is not None:
					mother, father = parts[mother_idx], parts[father_idx]                   
					candidate_vars_zygosity.append((gene, variant, transcript, variant_id, ref, alt, mother, father))
				candidate_vars.append((gene, variant, transcript, variant_id, zygosity))
		else:
			candidate_vars.append((gene, variant, transcript, variant_id, zygosity))

	def getZygosityFromVCF():
		gene_zygosity = dict()
		for item in candidate_vars_zygosity:
			gene, variant, transcript, variant_id, ref, alt, mother, father = item
			if gene in gene_zygosity:
				gene_zygosity[gene].append((ref, alt, mother, father)) 
			else:
				gene_zygosity[gene] = [(ref, alt, mother, father)]
	
		comp_het_genes = [] 
		for gene in gene_zygosity.keys():
			if len(gene_zygosity[gene]) > 1:
				var_from_mother, var_from_father = False, False
				for item in gene_zygosity[gene]:
					if mother == alt and father == ref:
						var_from_mother = True
					if mother == ref and father == alt:
						var_from_father = True
				if var_from_mother and var_from_father:
					comp_het_genes.append(gene)
		return comp_het_genes	

	if candidate_vars_zygosity:
		candidate_vars = []
        # if only one parent ngs data are available
        if parent_ngs in [1, 2]:
		    for item in candidate_vars_zygosity:
		    	gene, variant, transcript, variant_id, ref, alt, mother, father = item
                if mother == alt or father == alt:
                    zygosity = 'het'
                else:
                    zygosity = ''
		    	candidate_vars.append((gene, variant, transcript, variant_id, zygosity))
        else: 
		    comp_het_genes = getZygosityFromVCF()
		    for item in candidate_vars_zygosity:
			    gene, variant, transcript, variant_id, ref, alt, mother, father = item
    			if gene in comp_het_genes:
	    			zygosity = 'comp het'
		    	elif not mother or not father:
 			    	zygosity = 'hem'
			    else:
				    if mother == alt and father == alt:
					    zygosity = 'hom'
    				elif mother == ref and father == ref:
	    				zygosity = 'de novo'
		    		else:
			    		zygosity = 'het'
		    	candidate_vars.append((gene, variant, transcript, variant_id, zygosity))

	tmp_candidate_vars = []
	gene_zygosity = dict()
	for var in candidate_vars:
		gene, variant, transcript, variant_id, zygosity = var
		tmp_candidate_vars.append((gene, variant, transcript, variant_id))
		if variant_id:
			gene_zygosity[variant_id] = zygosity
		if gene and variant:
			gene_zygosity[(gene, variant)] = zygosity
	candidate_vars = tmp_candidate_vars

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
	return candidate_vars, CANDIDATE_GENES, df_genes, field_names, gene_zygosity 

def map_phenotype2gene(CANDIDATE_GENES, phenos, corner_cases, candidate_vars, original_phenos):
	ranking_genes, ranking_disease, gene_associated_phenos = map_phenotype_to_gene.generate_score(phenos, CANDIDATE_GENES, corner_cases, original_phenos)
	# gene_associated_phenos = dict(list) e.g., {'BRCA1':['breast..', '..'], 'PTPN11':['noonan', '..']}
	for gene in gene_associated_phenos.keys():
		phenos = gene_associated_phenos[gene]
		phenos = ', '.join(phenos)
		gene_associated_phenos[gene] = phenos
	df_gene_associated_phenos = pd.DataFrame(gene_associated_phenos.items(), columns = ['gene', 'correlated_phenotypes'])
	# collect variant info
	hpo_filtered_genes = np.unique([i[0] for i in ranking_genes]).tolist()

	tmp_candidate_vars = []
	for var in candidate_vars:
		if var[0] in hpo_filtered_genes:
			tmp_candidate_vars.append(var)
	candidate_vars = tmp_candidate_vars
	return ranking_genes, candidate_vars, df_gene_associated_phenos

def update_phenotype2gene(final_res, variants, ranking_genes, gene_zygosity, candidate_vars):
	ranking_genes = update_phenotype_to_gene.rankGenePhenoByCodingEffect(final_res, variants, ranking_genes)
	ranking_genes = update_phenotype_to_gene.rankGenePhenoByInheritancePattern(ranking_genes, gene_zygosity, candidate_vars)
	return ranking_genes

def master_function(raw_input_id):
	status_step = "generating candidate variants ..." 
	raw_input = Raw_input_table.objects.get(id=raw_input_id)
	input_gene = raw_input.raw_input_gene
	input_phenotype = raw_input.raw_input_phenotype
    # parent_ngs [0, 1, 2, 3]. 0 -- no parents NGS data; 1 -- only father's data; 2 -- only mother's data; 3 -- both parents' data
    parent_ngs = 0
    parent_affects = 0
    father_vcf = ''
    mother_vcf = ''
    incidental_finding_report = 0
    candidate_gene_report = 0

	# Read input pheno file and generate phenos and corner_cases 
	phenos, corner_cases, original_phenos, phenotype_translate = read_input_pheno_file(input_phenotype)

	# Read input gene file and generate candidate_vars. candidate_vars are (gene, variant, transcript, variant_id); CANDIDATE_GENES is a list of gene symbols; df_genes is a dataframe that keeps all the data that user uploaded; field_names are header of the input gene file 
	candidate_vars, CANDIDATE_GENES, df_genes, field_names, gene_zygosity = read_input_gene_file(input_gene, parent_ngs, father_vcf, mother_vcf)
	# print 'candidate_vars', candidate_vars
	# print 'CANDIDATE_GENES', CANDIDATE_GENES
	# print 'df_genes', df_genes
	# print 'field_names', field_names
	if not CANDIDATE_GENES:
		# collect variant info
		raw_input.status = "Annotating variants using genomic databases"
		raw_input.save()
		# candidate_vars from vcf file was updated, because gene, variant, transcript were empty
		final_res, variant, candidate_vars = collectVariantInfo.get_variants_from_vcf(candidate_vars)
		CANDIDATE_GENES = [_[0] for _ in final_res]
		# map phenotype to gene; the candidate_vars was filtered: if it is a gene associated with phenos, then keep it.
		if phenos:
			raw_input.status = "Maping phenotypes to genes"
			raw_input.save()
			ranking_genes, candidate_vars, df_gene_associated_phenos = map_phenotype2gene(CANDIDATE_GENES, phenos, corner_cases, candidate_vars, original_phenos)
		else:
			ranking_genes = []
			for key in variant.keys():
				gene, variant = key
				variant_id = variant[key][id]
				zygosity = gene_zygosity[variant_id]
				ranking_genes.append((gene, variant, 1.0, 1, 1.0, zygosity))
	else:
		# map phenotype to gene; the candidate_vars was filtered: if it is a gene associated with phenos, then keep it.
		if phenos:
			raw_input.status = "Maping phenotypes to genes"
			raw_input.save()
			ranking_genes, candidate_vars, df_gene_associated_phenos = map_phenotype2gene(CANDIDATE_GENES, phenos, corner_cases, candidate_vars, original_phenos)
		else:
			ranking_genes = []
			for key in gene_zygosity.keys():
				try:
					gene, variant = key
				except:
					continue
				zygosity = gene_zygosity[key]
				ranking_genes.append((gene, variant, 1.0, 1, 1.0, zygosity))
		# collect variant info
		raw_input.status = "Annotating variants using genomic databases"
		raw_input.save()
		final_res, variants = collectVariantInfo.get_variants(candidate_vars)
	# print 'ranking_genes', ranking_genes
	# print 'candidate_vars', candidate_vars
	# print 'final_res', final_res
	# print 'variants', variants

	if final_res == [] and variants == defaultdict(dict):
		return pd.DataFrame(), df_genes, phenos, field_names, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
	else:
		if phenos:
			# update phenotype correlation using coding effect and zygosity 
			ranking_genes = update_phenotype2gene(final_res, variants, ranking_genes, gene_zygosity, candidate_vars)
			df_ranking_genes = pd.DataFrame(ranking_genes, columns=['gene', 'variant', 'score_sim', 'hits', 'score', 'zygosity'])
			df_ranking_genes = df_ranking_genes[['gene', 'variant', 'score', 'zygosity']]
			df_ranking_genes = df_ranking_genes.merge(df_gene_associated_phenos, on = 'gene', how = 'left')
			df_ranking_genes.sort_values(by=['score'], ascending = [0], inplace = True)
			df_hpo_ranking_genes = df_ranking_genes[['gene', 'variant', 'score']] 
		else:
			df_hpo_ranking_genes = pd.DataFrame(ranking_genes, columns=['gene', 'variant', 'score_sim', 'hits', 'score', 'zygosity'])
			df_ranking_genes = df_hpo_ranking_genes[['gene', 'variant', 'score_sim', 'hits', 'score', 'zygosity']]
			df_ranking_genes['score_sim'] = np.nan
			df_ranking_genes['hits'] = np.nan
			df_ranking_genes['score'] = np.nan
			df_hpo_ranking_genes = df_hpo_ranking_genes[['gene', 'variant', 'score']]

		# pubmed
		raw_input.status = "Searching biomedical literatures"
		raw_input.save()
		df_pubmed = pubmed.queryPubmedDB(final_res)

		# ACMG
		raw_input.status = "Checking ACMG standard"
		raw_input.save()

		ACMG_result, variant_ACMG_interpretation, variant_ACMG_interpret_chinese, df_variant_ACMG_interpret, df_variant_ACMG_interpret_chinese = ACMG.Get_ACMG_result(df_hpo_ranking_genes, variants, df_pubmed)

		# filter variant on phenotype

		if phenos:
			raw_input.status = "Filtering variants based on phenotypes"
			raw_input.save()
			df_final_res, variant_ACMG_interpretation, variant_ACMG_interpret_chinese = filterVariantOnPhenotype.generateOutput(variants, ACMG_result, phenos, variant_ACMG_interpretation, variant_ACMG_interpret_chinese)
			# df_final_res = df_final_res.merge(df_gene_associated_phenos, on = 'gene', how = 'left')
			df_ranking_genes = df_ranking_genes[['gene', 'zygosity', 'correlated_phenotypes']]
			df_final_res = df_final_res.merge(df_ranking_genes, on = 'gene', how = 'left')
			df_final_res = df_final_res[['gene', 'id', 'variant', 'zygosity','correlated_phenotypes', 'pheno_match_score', 'hit_criteria', 'pathogenicity', 'final_score']]
			# if phenos are provided, we return a df_ranking_genes dataframe, which contains 'gene', 'variant', 'score_sim', 'hits', 'score', 'zygosity', 'associated_phenotypes'
			return df_final_res, df_genes, phenos, field_names, variant_ACMG_interpretation, variant_ACMG_interpret_chinese, df_ranking_genes

		else:
			df_ranking_genes = df_ranking_genes[['gene', 'zygosity']]
			ACMG_result = ACMG_result.merge(df_ranking_genes, on = 'gene', how = 'left')
			return ACMG_result, df_genes, phenos, field_names, df_variant_ACMG_interpret, df_variant_ACMG_interpret_chinese, df_ranking_genes

