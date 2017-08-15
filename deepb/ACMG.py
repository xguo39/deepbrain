# -*- coding: utf-8 -*-

import re
import pandas as pd
from collections import defaultdict
import pickle
import amino_acid_mapping
import numpy as np
import os
import random
import time
import sys
from google import google
import MySQLdb

BASE = os.path.dirname(os.path.abspath(__file__))

reload(sys)
sys.setdefaultencoding('utf-8')

def getKnownGeneCanonical():
    global knownGeneCanonical
    knownGeneCanonical = dict()
    df_knownGeneCanonical = pd.read_csv(os.path.join(BASE, 'data/ACMG/knownGeneCanonical.txt'), sep = ' ', dtype = str)
    df_ucsc_refseq_map = pd.read_csv(os.path.join(BASE, 'data/ACMG/kgTxInfo.txt'), usecols = [0, 2], names = ['Transcript(ucsc/known)', 'Transcript(HGVS)'], sep = '\t')
    df_knownGeneCanonical = df_knownGeneCanonical.merge(df_ucsc_refseq_map, how = 'left', on = 'Transcript(ucsc/known)')
    for index, row in df_knownGeneCanonical.iterrows():
        transcript = row['Transcript(HGVS)']
        num_exons = row['exons']
        transcript_start = row['start']
        transcript_end = row['end']
        knownGeneCanonical[transcript] = (num_exons, transcript_start, transcript_end) 

def getLOFGenes():
    global LOF_genes
    df_LOF_genes = pd.read_csv(os.path.join(BASE, 'data/ACMG/PVS1.LOF.genes.txt'), names = ['gene'])
    LOF_genes = pd.unique(df_LOF_genes.gene.values).tolist()
    #infile = open('data/lof_gene_and_non_lof_gene.p', 'rb')
    #LOF_genes, non_LOF_genes = pickle.load(infile)
    #infile.close()

def getNullVariantLOF():
    global null_variant_lof
    null_variant_lof = dict()
    df_null_variant_lof = pd.read_csv(os.path.join(BASE, 'data/ACMG/null_variant_lof_pathogenicity.txt'), usecols = [0, 1, 3, 5], sep = '\t')
    for index, row in df_null_variant_lof.iterrows():
        gene, transcript, cDNA_pos, variation_ids = row['gene'], row['transcript'], row['pos'], row['variation_ids']
        if (gene, transcript) not in null_variant_lof:
            null_variant_lof[(gene, transcript)] = [(cDNA_pos, variation_ids)]
        else:
            null_variant_lof[(gene, transcript)].append((cDNA_pos, variation_ids))

def check_PVS1(variant_):
    '''
    Certain types of variants (e.g., nonsense, frameshift, canonical
    +- 1 or 2 splice sites, initiation codon, single exon or multiexon
    deletion) in a gene where LOF is a known mechanism of disease
    '''
    # Need variant effect (nonsense, frameshift, ...); canonical transcript; 
    # LOF genes; splicing prediction score; allele start position; exon (from cadd)
    curr_interpret, curr_interpret_chinese = [], []
    gene, variant_effect, transcript, exon, variant_id = variant_['gene'], variant_['effect'], variant_['transcript'], variant_['exon'], variant_['id']
    cDNA = variant_['variant']
    dbscSNV_rf_score, dbscSNV_ada_score = variant_['dbscSNV_rf_score'], variant_['dbscSNV_ada_score']
    if variant_id:
        allele_start_pos = re.match(r'[0-9]{1,20}', variant_id.split('.')[-1]).group(0)
    else:
        return 0
    null_variant_types = ["chromosome", "exon_loss", "frameshift", "inversion", "feature_ablation", "gene_fusion", "rearranged_at_DNA_level", "initiator_condon", "splice_acceptor", "splice_donor", "stop_gain", 'start_lost', 'stop_lost']
 
    PVS1 = 0
    dbscSNV_cutoff = 0.6
    #effect_in_null_variant_types = re.search('|'.join(null_variant_types), variant_effect, re.I) and not re.search('intron', variant_effect, re.I)
    effect_in_null_variant_types = re.search('|'.join(null_variant_types), variant_effect, re.I)
    in_LOF_genes = True if gene in LOF_genes else False
    #not_affect_splicing = False if ((dbscSNV_rf_score and float(dbscSNV_rf_score) > dbscSNV_cutoff) or (dbscSNV_ada_score and float(dbscSNV_ada_score) > dbscSNV_cutoff)) else True 
    #not_benign_splicing = True if ((not dbscSNV_rf_score and not dbscSNV_ada_score) or (dbscSNV_rf_score and float(dbscSNV_rf_score) > dbscSNV_cutoff) or (dbscSNV_ada_score and float(dbscSNV_ada_score) > dbscSNV_cutoff)) else False 
    not_benign_splicing = True if ((dbscSNV_rf_score and float(dbscSNV_rf_score) > dbscSNV_cutoff) or (dbscSNV_ada_score and float(dbscSNV_ada_score) > dbscSNV_cutoff)) else False 
    curr_interpret.append('It is null variant.') if effect_in_null_variant_types else curr_interpret.append('It is NOT null variant.') 
    curr_interpret_chinese.append('基因变异类型是无效变异(null variant).') if effect_in_null_variant_types else curr_interpret_chinese.append('基因变异类型不是无效变异(null variant).') 
    ## 如果coding effect是null variant，查看这个variant downstream（同一gene 同一transcript）有没有null variation 且 pathogenic
    downstream_null_lof_pathogenic = False
    if re.match(r'c\.-', cDNA):
        cDNA_pos = 0
    elif re.search(r'\*', cDNA):
        cDNA_pos = 100000000
    else:
        cDNA_pos = re.search(r'[0-9]{1,10}', cDNA).group() 
    if (gene, transcript) in null_variant_lof:
        values = null_variant_lof[(gene, transcript)] 
        for value in values:
            downstream_cDNA_pos, variation_ids = value
            if int(downstream_cDNA_pos) > int(cDNA_pos):
                downstream_null_lof_pathogenic = True
    if effect_in_null_variant_types and downstream_null_lof_pathogenic:
        PVS1 = 1 
        curr_interpret.append('There is a pathogenic null variant downstream in the same gene.' ) 
        curr_interpret_chinese.append('突变位点的下游含有致病的无效变异（null variant）.' ) 
 
    if effect_in_null_variant_types:
        curr_interpret.append('Allele in a gene where loss of function (LOF) is a known mechanism of disease.') if in_LOF_genes else curr_interpret.append('Allele in a gene where loss of function (LOF) is NOT a known mechanism of disease.') 
        curr_interpret_chinese.append('变异位点所在基因的功能丢失(loss of function)是已知的致病机制.') if in_LOF_genes else curr_interpret_chinese.append('变异位点所在基因的功能丢失(loss of function)不是已知的致病机制.') 

    # google_input = gene+' loss of function'
    # search_results = google.search(google_input, 1)
    # lof = 0
    # for i in search_results:
    #     for j in i.description.split("..."):
    #         j = j.replace("\n", "")
    #         if (gene in j) and (re.search(r'\bloss-of-function\b|\bloss of function\b', j, re.I) or re.search(r'\bLOF\b', j)) and not re.search(r'\bno\b|\bnot\b|\bwhether\b', j, re.I):
    #             lof = 1
    #             break
    #     else:
    #         continue
    #     break
    # if lof == 1:
    #     curr_interpret.append('Allele in a gene where loss of function (LOF) is a known mechanism of disease.')
    #     curr_interpret_chinese.append('变异位点所在基因的功能丢失(loss of function)是已知的致病机制.')
    # else:
    #     curr_interpret.append('Variant NOT in null variant type.')
    #     curr_interpret_chinese.append('基因变异类型不是无效变异(null variant).')
    if effect_in_null_variant_types: 
        curr_interpret.append('The variant has damaging splicing effect.') if not_benign_splicing else curr_interpret.append('The variant does NOT have damaging splicing effect.') 
        curr_interpret_chinese.append('此变异具有有害的剪接效应(splicing effect).') if not_benign_splicing else curr_interpret_chinese.append('此变异不具有有害的剪接效应(splicing effect).') 

    #if effect_in_null_variant_types and in_LOF_genes and not_affect_splicing: PVS1 = 1
    if effect_in_null_variant_types and in_LOF_genes and not_benign_splicing: PVS1 = 1
    if transcript in knownGeneCanonical and effect_in_null_variant_types:
        num_exons, transcript_end = knownGeneCanonical[transcript][0], knownGeneCanonical[transcript][2]
        if exon == 1 or exon == num_exons: 
            PVS1 = 0
            if exon == 1: 
                curr_interpret.append('The allele is in the first exon.')
                curr_interpret_chinese.append('变异发生在第一个外显子上.')
            if exon == num_exons: 
                curr_interpret.append('The allele is in the last exon.')
                curr_interpret_chinese.append('变异发生在最后一个外显子上.')
        if (float(transcript_end) - float(allele_start_pos)) < 50: 
            PVS1 = 0
            curr_interpret.append('The allele is within 50 nucleotides of the final exon-junction complex.')
            curr_interpret_chinese.append('变异位点距离最后一个外显子末端在50个核苷酸碱基对内.')
    curr_interpret.append('PVS1 is met.') if PVS1 == 1 else curr_interpret.append('PVS1 is NOT met.')
    curr_interpret_chinese.append('符合PVS1标准.') if PVS1 == 1 else curr_interpret_chinese.append('不符合PVS1标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PVS1', curr_interpret))
    interpret_chinese.append(('PVS1', curr_interpret_chinese))
    return PVS1

def getMissenseAAPathogenicity(): 
    global missense_AA_pathogenicity, missense_original_AA
    missense_AA_pathogenicity, missense_original_AA = defaultdict(dict), defaultdict(dict)
    with open(os.path.join(BASE, 'data/ACMG/missense_AA_change_pathogenicity.txt'), 'rU') as f:
        f.readline()
        for line in f:
            line = line.rstrip('\n')
            parts = line.split('\t')
            gene, protein, clinvar_id = parts[0], parts[1], parts[3]
            clinvar_id = "<a href='https://www.ncbi.nlm.nih.gov/clinvar/variation/%s/'> %s </a>" %(clinvar_id, clinvar_id)
            try:
                original_AA = re.match(r'p\.[A-Za-z]{3}[0-9]{1,10}', protein).group(0)
            except AttributeError:
                protein_map = amino_acid_mapping.map1to3
                robj = re.compile('|'.join(protein_map.keys()))
                protein = robj.sub(lambda m: protein_map[m.group(0)], protein)
                try:
                    original_AA = re.match(r'p\.[A-Za-z]{3}[0-9]{1,10}', protein).group(0)
                except AttributeError:
                    original_AA = re.match(r'p\.\*[0-9]{1,10}', protein).group(0)
            if gene in missense_AA_pathogenicity and protein in missense_AA_pathogenicity[gene]:
                missense_AA_pathogenicity[gene][protein].append(clinvar_id) 
                missense_original_AA[gene][original_AA].append((clinvar_id, protein))
            else:
                missense_AA_pathogenicity[gene][protein] = [clinvar_id]
                missense_original_AA[gene][original_AA] = [(clinvar_id, protein)]

def check_PS1_PM5(variant_):
    '''
    PS1 Same amino acid change as a previously established pathogenic variant regardless of nucleotide change
    Example: Val->Leu caused by either G>C or G>T in the same codon
    Novel missense change at an amino acid residue where a different missense change determined to be
    pathogenic has been seen before;Example: Arg156His is pathogenic; now you observe Arg156Cy
    '''
    # Need a file built from Clinvar Gene|ProteinChange|Pathogenicity; also add pubmed searched results later
    curr_interpret, curr_interpret_chinese = [], []
    gene, variant_effect, protein = variant_['gene'], variant_['effect'], variant_['protein']
    dbscSNV_rf_score, dbscSNV_ada_score = variant_['dbscSNV_rf_score'], variant_['dbscSNV_ada_score']
    missense_variant_types = ["missense", "rare_amino_acid_variant"]
    try:
        original_AA = re.match(r'p\.[A-Za-z]{3}[0-9]{1,10}', protein).group(0)
    except AttributeError:
        original_AA = ''

    PS1, PM5 = 0, 0
    dbscSNV_cutoff = 0.6
    effect_in_missense_variant_types = re.search('|'.join(missense_variant_types), variant_effect, re.I)
    curr_interpret.append('Coding effect is missense.') if effect_in_missense_variant_types else curr_interpret.append('Coding effect is NOT missense.')
    curr_interpret_chinese.append('变异为错义突变 (missense).') if effect_in_missense_variant_types else curr_interpret_chinese.append('变异非错义突变.')
    has_pathogenic_same_AA_change, has_pathogenic_different_AA_change = False, False 
    if gene in missense_AA_pathogenicity and protein in missense_AA_pathogenicity[gene]:
        has_pathogenic_same_AA_change = True
        clinvar_ids = missense_AA_pathogenicity[gene][protein]
        clinvar_ids = ', '.join(clinvar_ids)
        curr_interpret.append('Same amino acid change as a previously established pathogenic variant regardless of nucleotide change (Clinvar references: %s).' % clinvar_ids)
        curr_interpret_chinese.append('之前报道导致相同氨基酸改变的基因变异被证明是致病的 (Clinvar数据库参考: %s).' % clinvar_ids)
    if gene in missense_original_AA and original_AA in missense_original_AA[gene]:
        clinvar_ids, different_proteins = [], []
        for tup in missense_original_AA[gene][original_AA]:
            if protein != tup[1]:
                has_pathogenic_different_AA_change = True
                clinvar_ids.append(tup[0])
                different_proteins.append(tup[1])
        if different_proteins:
            clinvar_ids = ', '.join(clinvar_ids)
            different_proteins = ', '.join(different_proteins)
            curr_interpret.append('Novel missense change at an amino acid residue where a different missense change (%s) determined to be pathogenic has been seen before (Clinvar references: %s).' % (different_proteins, clinvar_ids))
            curr_interpret_chinese.append('此错义突变 (missense) 发生在的氨基酸残基在之前发现过致病错义突变(%s)，尽管是不同氨基酸改变 (Clinvar数据库参考: %s).' % (different_proteins, clinvar_ids))

    not_affect_splicing = False if ((dbscSNV_rf_score and float(dbscSNV_rf_score) > dbscSNV_cutoff) or (dbscSNV_ada_score and float(dbscSNV_ada_score) > dbscSNV_cutoff)) else True
    if not has_pathogenic_same_AA_change: curr_interpret.append('Not find same amino acid change as a previously established pathogenic variant.')
    if not has_pathogenic_same_AA_change: curr_interpret_chinese.append('未发现之前报道导致相同氨基酸改变的致病基因变异.')
    if not has_pathogenic_different_AA_change: curr_interpret.append('Not find missense change at an amino acid residue where a different missense change determined to be pathogenic has been seen before.')
    if not has_pathogenic_different_AA_change: curr_interpret_chinese.append('未发现导致相同氨基酸残基错义突变（不同氨基酸改变）导致的致病基因变异.')
    curr_interpret.append('The variant does NOT have damaging splicing effect.') if not_affect_splicing else curr_interpret.append('The variant has damaging splicing effect.') 
    curr_interpret_chinese.append('此变异不具有害的剪接效应(splicing effect).') if not_affect_splicing else curr_interpret_chinese.append('此变异具有有害的剪接效应(splicing effect).') 
    if effect_in_missense_variant_types and has_pathogenic_same_AA_change and not_affect_splicing: PS1 = 1
    if effect_in_missense_variant_types and has_pathogenic_different_AA_change: PM5 = 1

    ## check pubmed articles if no data in clinvar
    if not variant_['clinvar_pathogenicity']:
        gene, variant = variant_['gene'], variant_['variant']
        if (gene, variant) in pubmed_studies:
            study_records = pubmed_studies[(gene, variant)]
            pathogenicity_score = np.mean([_[1] for _ in study_records])
            pmids = [_[2] for _ in study_records]
            variant_pubmed_articles = pubmed_articles[(gene, variant)]
            # Get info of each pmid article
            pubmed_article_info = []
            for pmid_ in pmids:
                for article_info in variant_pubmed_articles:
                    pmid, title, journal, year, impact_factor = article_info
                    if pmid == pmid_:
                        pubmed_article_info.append("<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'> %s </a>: title: %s, journal: %s, year: %s, impact_factor: %s" %(pmid, pmid, title, journal, year, impact_factor))  
            PS1 = pathogenicity_score
            curr_interpret.append('The variant was reported in literatures (PMIDs: %s) and the pathogenicity score (0-1) is %s.' % ('; '.join(pubmed_article_info), str(PS1))) 
            curr_interpret_chinese.append('此基因变异曾被之前生物医学文献报道 (PMIDs: %s)，致病性分数 (0-1) 为%s.' % ('; '.join(pubmed_article_info), str(PS1))) 

    curr_interpret.append('PS1 is met.') if PS1 == 1 else curr_interpret.append('PS1 is NOT met.')
    curr_interpret_chinese.append('符合PS1标准.') if PS1 == 1 else curr_interpret_chinese.append('不符合PS1标准.')
    curr_interpret.append('PM5 is met.') if PM5 == 1 else curr_interpret.append('PM5 is NOT met.')
    curr_interpret_chinese.append('符合PM5标准.') if PM5 == 1 else curr_interpret_chinese.append('不符合PM5标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PS1 and PM5', curr_interpret))
    interpret_chinese.append(('PS1和PM5', curr_interpret_chinese))
    return PS1, PM5

def getDeNovoGenes():
    global denovo_genes, non_denovo_genes
    infile = open(os.path.join(BASE, 'data/denovo_gene_and_non_denovo_gene.p'), 'rb')
    denovo_genes, non_denovo_genes = pickle.load(infile)
    infile.close()

def check_PS2_PM6(variant_, parent_ngs, parent_affects):
    '''
    De novo (both maternity and paternity confirmed) in a patient with the disease and no family history
    Assumed de novo, but without confirmation of paternity and maternity
    '''
    curr_interpret, curr_interpret_chinese = [],[]
    gene, zygosity = variant_['gene'], variant_['zygosity']
    PS2, PM6 = 0, 0
    if parent_ngs !=0 and parent_affects != 0:
        if parent_ngs == 1:
            curr_interpret.append('Only father NGS data are available.') 
            curr_interpret_chinese.append('只有父亲的基因测序数据.') 
        elif parent_ngs == 2:   
            curr_interpret.append('Only mother NGS data are available.')
            curr_interpret_chinese.append('只有母亲的基因测序数据.')
        else:
            curr_interpret.append('Both father and mother NGS data are available.')
            curr_interpret_chinese.append('父亲和母亲的基因测序数据都有.')
        if parent_affects == 1: 
            curr_interpret.append('Father was affected.')
            curr_interpret_chinese.append('父亲有相似表型.')
        elif parent_affects == 2: 
            curr_interpret.append('Mother was affected.')
            curr_interpret_chinese.append('母亲有相似表型.')
        else:
            curr_interpret.append('Both father and mother were affected.')
            curr_interpret_chinese.append('父亲和母亲都有相似表型.')
        if zygosity == 'de novo':
            curr_interpret.append('The variant is De Novo.')
            curr_interpret_chinese.append('此变异是新生突变（De Novo）.')
            de_novo_is_known_mechanism = False
            if gene in denovo_genes:
                de_novo_is_known_mechanism = True
            if de_novo_is_known_mechanism:
                PS2 = 1
                curr_interpret.append('De Novo is a known pathogenicity mechanism of the gene.')
                curr_interpret_chinese.append('新生突变（De Novo）是此基因的已知致病机制.')
            else:
                PS2 = 0.5 
                curr_interpret.append('De Novo is not a known pathogenicity mechanism of the gene.')
                curr_interpret_chinese.append('新生突变（De Novo）不是此基因的已知致病机制.')
    elif parent_ngs == 0:
        curr_interpret.append('No parents NGS data are available.')
        curr_interpret_chinese.append('没有父亲和母亲的基因测序数据.')
    elif parent_affects == 0:
        curr_interpret.append('No information were provided whether the parents were affected.')
        curr_interpret_chinese.append('没有提供父亲和母亲是否具有相似表型的信息.')
    if zygosity == 'de novo':
        PM6 = 1
    curr_interpret.append('PS2 is met.') if PS2 != 0 else curr_interpret.append('PS2 is NOT met.')
    curr_interpret_chinese.append('符合PS2标准.') if PS2 != 0 else curr_interpret.append('不符合PS2标准.')
    curr_interpret.append('PM6 is met.') if PM6 == 1 else curr_interpret.append('PM6 is NOT met.')
    curr_interpret_chinese.append('符合PM6标准.') if PM6 == 1 else curr_interpret.append('不符合PM6标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PS2 and PM6', curr_interpret))
    interpret_chinese.append(('PS2和PM6', curr_interpret_chinese))
    return PS2, PM6

def checkFunctionalStudy(title, text, impactfactor):
    functional_study_keywords = ['function', 'in vivo', 'in vitro', 'RNA', 'mouse', 'mice', 'rodent', 'rat', 'zebrafish', 'frog', 'patient', 'cases', 'diagnos', 'structur', 'enzyme activit', 'segregation', 'pedigree', 'protein defect', 'protein function', 'protein expression', 'rt-pcr']
    count = 0
    for keyword in functional_study_keywords:
        if keyword == 'RNA':
            if re.search(keyword, title) or re.search(keyword, text):
                count += 1
            continue 
        if keyword == 'rat':
            if re.search(r'\brat\b|\brats\b', title) or re.search(r'\brat\b|\brats\b', text, re.I):
                count += 1
            continue 
        if re.search(keyword, title, re.I) or re.search(keyword, text, re.I):
            count += 1 
    if impactfactor: 
        impactfactor = float(impactfactor)
    else:
        impactfactor = 0.5 
    weighted_count = count * np.log(impactfactor + 1.0) 
    return count, weighted_count

def getPubMedEval(df_pubmed):
    global functional_study_pathogenicity, study_pathogenicity_score, pubmed_studies, functional_pubmed_studies 
    functional_study_pathogenicity = dict()
    study_pathogenicity_score = dict()
    pubmed_studies, functional_pubmed_studies = dict(), dict()
    res = defaultdict(dict)
    functional_study_res = dict()
    for index, row in df_pubmed.iterrows():
        gene, variant, pathogenicity_score, impactfactor, year, title, text, pmid = row['Gene'], row['Variant'], row['pathogenicity_score'], row['Impact_Factor'], row['Year'], row['Title'], row['Abstract'], row['PMID']
        plain_pmid = pmid
        pmid = "<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'> %s </a>" %(pmid, pmid)
        count, weighted_count = checkFunctionalStudy(title, text, impactfactor)
        if (gene, variant) not in study_pathogenicity_score: 
            study_pathogenicity_score[(gene,variant)] = [pathogenicity_score]
            pubmed_studies[(gene, variant)] = [(pmid, pathogenicity_score, plain_pmid)]
        else:
            study_pathogenicity_score[(gene,variant)].append(pathogenicity_score)
            pubmed_studies[(gene, variant)].append((pmid, pathogenicity_score, plain_pmid))
        # Check if it is well-established functional study 
        isFunctionalStudy = True if (count >=2 and weighted_count >= 4) else False 
        if isFunctionalStudy: 
            if (gene, variant) not in functional_study_res:
                functional_study_res[(gene, variant)] = [pathogenicity_score]
                functional_pubmed_studies[(gene, variant)] = [pmid]
            else:
                functional_study_res[(gene, variant)].append(pathogenicity_score)
                functional_pubmed_studies[(gene, variant)].append(pmid)
    # print study_pathogenicity_score
    for key in functional_study_res.keys():
        pathogenicity_prob = np.mean(functional_study_res[key])
        study_pathogenicity_score[key] = np.mean(study_pathogenicity_score[key])
        if pathogenicity_prob > 0.9: functional_study_pathogenicity[key] = 'P' 
        if pathogenicity_prob < 0.3: functional_study_pathogenicity[key] = 'B'
    for key in study_pathogenicity_score.keys():
        study_pathogenicity_score[key] = np.mean(study_pathogenicity_score[key])

def check_PS3_BS3(variant_):
    '''
    Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene
    product
    Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing
    '''
    # use clinvar derived pubmed articles and then search pubmed database
    curr_interpret, curr_interpret_chinese = [],[]
    gene, variant = variant_['gene'], variant_['variant']

    PS3, BS3 = 0, 0
    if (gene, variant) in functional_study_pathogenicity:
        pmids = functional_pubmed_studies[(gene, variant)]
        # print pmids
        if functional_study_pathogenicity[(gene, variant)] == 'P': 
            PS3 = 1
            curr_interpret.append('Well-established functional studies supportive of a damaging effect of the variant (PMIDs: %s).' % (','.join(pmids)))
            curr_interpret_chinese.append('完善的体内或体外功能性研究支持此基因变异的致病性 (PMIDs: %s).' % (','.join(pmids)))
        if functional_study_pathogenicity[(gene, variant)] == 'B': 
            BS3 = 1
            curr_interpret.append('Well-established functional studies show no damaging effect of the variant (PMIDs: %s).' % (','.join(pmids)))
            curr_interpret_chinese.append('完善的体内或体外功能性研究表明此基因变异并未损害蛋白功能或影响剪接 (PMIDs: %s).' % (','.join(pmids)))
    else:
        curr_interpret.append('Not find well-established functional studies on this variant.')
        curr_interpret_chinese.append('未发现针对此基因变异的完善的体内或体外功能性研究.')
    curr_interpret.append('PS3 is met.') if PS3 == 1 else curr_interpret.append('PS3 is NOT met.')
    curr_interpret_chinese.append('符合PS3标准.') if PS3 == 1 else curr_interpret_chinese.append('不符合PS3标准.')
    curr_interpret.append('BS3 is met.') if BS3 == 1 else curr_interpret.append('BS3 is NOT met.')
    curr_interpret_chinese.append('符合BS3标准.') if BS3 == 1 else curr_interpret_chinese.append('不符合BS3标准.')
    curr_interpret = ' '.join(curr_interpret)
    interpret.append(('PS3 and BS3', curr_interpret))
    interpret_chinese.append(('PS3和BS3', curr_interpret_chinese))
    return PS3, BS3 

def getORGreaterThan5Variants():
    # OR -- odds ratios or relative risk
    global variants_with_or_greater_than_5
    variants_with_or_greater_than_5 = []
    with open(os.path.join(BASE, 'data/ACMG/PS4.variants.hg19.txt'), 'rb') as f:
        f.readline()
        for line in f:
            line = line.rstrip()
            parts = line.split('\t')
            variant = 'chr' + parts[0] + '_' + parts[1] + '_' + parts[1] + '_' + parts[3] + '_' + parts[4]  
            variants_with_or_greater_than_5.append(variant)
    #print variants_with_or_greater_than_5

def check_PS4_bak(variant_):
    '''
    The prevalence of the variant in affected individuals is significantly increased compared with the prevalence
    in controls; OR>5 in all the gwas, the dataset is from gwasdb jjwanglab.org/gwasdb
    '''
    # use vcf annoation (ref, alt) from myvariant
    curr_interpret, curr_interpret_chinese = [],[]
    gene, variant_ref, variant_alt, variant_id = variant_['gene'], variant_['ref'], variant_['alt'], variant_['id']
    if variant_id:
        allele_start_end_pos = re.findall(r'[0-9]{1,20}', variant_id.split('.')[-1])
    else:
        return 0 
    if len(allele_start_end_pos) == 1:
        allele_start_pos = allele_end_pos = allele_start_end_pos[0]
    elif len(allele_start_end_pos) == 2:
        allele_start_pos, allele_end_pos = allele_start_end_pos
    # e.g., chr1_2068906_2068906_G_T
    variant = variant_id.split(':')[0] + '_' + allele_start_pos + '_' + allele_end_pos + '_' + variant_ref + '_' + variant_alt 
    PS4 = 0
    if PS4 in variants_with_or_greater_than_5: 
        PS4 = 1
        curr_interpret.append('Relative risk is greater than 5. The prevalence of the variant in affected individuals is significantly increased compared with the prevalence in controls.')
        curr_interpret_chinese.append('具有此基因变异的人群患病率显著升高，相对风险(Relative Risk)大于5.0.')
    else:
        curr_interpret.append('Relative risk is smaller than 5. The prevalence of the variant in affected individuals is NOT significantly increased compared with the prevalence in controls.')
        curr_interpret_chinese.append('具有此基因变异的人群患病率并未显著升高，相对风险(Relative Risk)小于5.0..')
    curr_interpret.append('PS4 is met.') if PS4 == 1 else curr_interpret.append('PS4 is NOT met.')
    curr_interpret_chinese.append('符合PS4标准.') if PS4 == 1 else curr_interpret_chinese.append('不符合PS4标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PS4', curr_interpret))
    interpret_chinese.append(('PS4', curr_interpret_chinese))
    return PS4

def getDominantRecessiveDiseaseNames():
    global dominant_diseases, recessive_diseases
    infile = open(os.path.join(BASE, 'data/disease_inheritance.p'), 'rb')
    dominant_diseases, recessive_diseases = pickle.load(infile)
    infile.close() 

def getDiseasePrevalence():
    # disease_prevalence is a dict with disease name (lower case) as key and prevalence as value
    global disease_prevalence
    infile = open(os.path.join(BASE, 'data/disease_prevalence.p'), 'rb')
    disease_prevalence = pickle.load(infile)
    infile.close() 

def calculateFreqFromPrevalence(disease, disease_is_dominant, disease_is_recessive):
    if disease not in disease_prevalence.keys():
        return None, None
    elif not disease_prevalence[disease]:
        return None, None
    else:
        if not disease_is_recessive and not disease_is_dominant:
            return None, None
        freq = []
        if disease_is_recessive:
            freq.append(np.sqrt(float(disease_prevalence[disease])))
        if disease_is_dominant:
            #freq.append(1 - np.sqrt(1- disease_prevalence[disease])) 
            freq.append(float(disease_prevalence[disease])) 
        return max(freq), disease_prevalence[disease]

def check_PS4(variant_):
    '''
    The prevalence of the variant in affected individuals is significantly increased compared with the prevalence
    in controls; OR>5 in all the gwas, the dataset is from gwasdb jjwanglab.org/gwasdb
    '''
    global max_freq # this variable will also be used in BS1 check
    curr_interpret, curr_interpret_chinese = [],[]
    gene = variant_['gene']
    clinvar_diseases = variant_['clinvar_associated_diseases']
    maf_exac = variant_['maf_exac']
    PS4 = 0
    disease_is_dominant, disease_is_recessive = False, False
    clinvar_diseases = clinvar_diseases.split('|')
    max_prevalence, max_disease, max_freq, max_PS4 = 0, None, None, 0
    for disease in clinvar_diseases:
        disease = disease.lower()
        if disease in dominant_diseases:
            disease_is_dominant = True
        if disease in recessive_diseases:
            disease_is_recessive = True
        freq, prevalence = calculateFreqFromPrevalence(disease, disease_is_dominant, disease_is_recessive)
        if maf_exac and freq and float(freq) > 5 * float(maf_exac):
            PS4 = 1
        elif maf_exac and freq and float(freq) > float(maf_exac):
            PS4 = float(freq) / (5.0 * float(maf_exac))
        if prevalence > max_prevalence:
            max_prevalence = prevalence
            max_disease = disease
            max_freq = freq 
            max_PS4 = PS4

    if max_prevalence > 0:
        curr_interpret.append('The prevalence for the disease %s is: %s.' % (str(max_prevalence), max_disease))
        curr_interpret_chinese.append('疾病%s盛行率是: %s.' % (str(max_prevalence), max_disease))
    else:
        curr_interpret.append('The prevalence data are not found.')
        curr_interpret_chinese.append('未找到相关疾病盛行率报道数据.')
    if maf_exac:
        curr_interpret.append('The EXAC MAF is: %s.' % (maf_exac))
        curr_interpret_chinese.append('EXAC最小等位基因频率(MAF): %s.' % (maf_exac))
    else:
        curr_interpret.append('The EXAC does not have MAF data for this allele.')
        curr_interpret_chinese.append('未找到EXAC最小等位基因频率(MAF)数据.')
    if max_PS4 > 0:
        curr_interpret.append('The prevalence of the variant in affected individuals is increased compared with the prevalence in controls: %s vs. %s.' % (str(max_freq), maf_exac))
        curr_interpret_chinese.append('变异出现在患病群体中的频率显著高于对照群体: %s vs. %s.' % (str(max_freq), maf_exac))
        curr_interpret.append('PS4 is met.') if max_PS4 == 1 else curr_interpret.append('PS4 is partially met.')
        curr_interpret_chinese.append('符合PS4标准.') if PS4 == 1 else curr_interpret_chinese.append('部分符合PS4标准.')
    else:
        curr_interpret.append('PS4 is not met.') 
        curr_interpret_chinese.append('不符合PS4标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PS4', curr_interpret))
    interpret_chinese.append(('PS4', curr_interpret_chinese))
    return PS4

def getRecessiveDominantGenes():
    global dominant_genes, recessive_genes, adultonset_genes
    df_omim_mim2gene = pd.read_csv(os.path.join(BASE, 'data/ACMG/omim_mim2gene.txt'), sep = '\t', skiprows = 1, usecols = [0, 1, 3], names = ['mim', 'type', 'gene']) 
    df_mim_dominant = pd.read_csv(os.path.join(BASE, 'data/ACMG/mim_domin.txt'), names = ['mim'])
    df_mim_recessive = pd.read_csv(os.path.join(BASE, 'data/ACMG/mim_recessive.txt'), names = ['mim'])
    df_mim_adultonset = pd.read_csv(os.path.join(BASE, 'data/ACMG/mim_adultonset.txt'), names = ['mim'])
    df_mim_dominant = df_mim_dominant.merge(df_omim_mim2gene, how = 'left', on = 'mim')  
    df_mim_recessive = df_mim_recessive.merge(df_omim_mim2gene, how = 'left', on = 'mim')  
    df_mim_adultonset = df_mim_adultonset.merge(df_omim_mim2gene, how = 'left', on = 'mim')  
    dominant_genes = pd.unique(df_mim_dominant.gene.values).tolist()
    recessive_genes = pd.unique(df_mim_recessive.gene.values).tolist()
    adultonset_genes = pd.unique(df_mim_adultonset.gene.values).tolist()

def check_PM2(variant_):
    '''
    Absent from controls (or at extremely low frequency if recessive) (Table 6) in Exome Sequencing Project,
    1000 Genomes Project, or Exome Aggregation Consortium
    '''
    # use maf from exac, 1000 genomes, and esp6500
    curr_interpret, curr_interpret_chinese = [], []
    gene, variant_id = variant_['gene'], variant_['id']
    maf_exac, maf_1000g, maf_esp6500 = variant_['maf_exac'], variant_['maf_1000g'], variant_['maf_esp6500']

    if not variant_id: return 0

    PM2 = 0
    cutoff_maf = 0.0001
    if (not maf_exac) and (not maf_1000g) and (not maf_esp6500): # Absent from all three databases
        PM2 = 1
        curr_interpret.append('The variant is absent from all three MAF databases: ExAC, 1000Genomes, ESP6500.')
        curr_interpret_chinese.append('未在人类基因变异数据库(ExAC, 1000Genomes, ESP6500)中发现此变异.')    
    if maf_exac or maf_1000g or maf_esp6500:
        is_recessive = True if gene in recessive_genes else False
        has_low_freq = True
        if maf_exac and float(maf_exac) >= cutoff_maf: has_low_freq = False
        if maf_1000g and float(maf_1000g) >= cutoff_maf: has_low_freq = False
        if maf_esp6500 and float(maf_esp6500) >= cutoff_maf: has_low_freq = False
        if not is_recessive and has_low_freq:
            curr_interpret.append('The variant has an extremely low frequency with MAF < 0.5%, but NOT causes recessive diseases.')
            curr_interpret_chinese.append('此基因变异的最小等位基因频率(MAF)极低(< 0.5%)，但并不引发隐性遗传病.')        
        if is_recessive and not has_low_freq:
            curr_interpret.append('The variant causes recessive diseases, but NOT have an extremely low frequency with MAF < 0.5%.')
            curr_interpret_chinese.append('此基因变异的最小等位基因频率(MAF)较高(>= 0.5%)，且并不引发隐性遗传病.')        
        if not is_recessive and not has_low_freq:
            curr_interpret.append('The variant does NOT have an extremely low frequency with MAF < 0.5%, and NOT causes recessive diseases.')
            curr_interpret_chinese.append('此基因变异的最小等位基因频率(MAF)较高(>= 0.5%)，且并不引发隐性遗传病.')
        if is_recessive and has_low_freq:
            PM2 = 1
            curr_interpret.append('The variant causes recessive diseases and is at an extremely low frequency with MAF < 0.5%.')
            curr_interpret_chinese.append('此基因变异的最小等位基因频率(MAF)极低(< 0.5%)，且引发隐性遗传病')

    curr_interpret.append('PM2 is met.') if PM2 == 1 else curr_interpret.append('PM2 is NOT met.')
    curr_interpret_chinese.append('符合PM2标准.') if PM2 == 1 else curr_interpret_chinese.append('不符合PM2标准.')    
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PM2', curr_interpret))
    interpret_chinese.append(('PM2', curr_interpret_chinese))
    return PM2
 
def check_BA1_BS1_bak(variant_):
    '''
    BA1 Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation Consortium
    Allele frequency is greater than expected for disorder 
    '''
    curr_interpret, curr_interpret_chinese = [], []
    maf_exac, maf_1000g, maf_esp6500 = variant_['maf_exac'], variant_['maf_1000g'], variant_['maf_esp6500']
    BA1, BS1 = 0, 0
    cutoff_BA1, cutoff_BS1 = 0.05, 0.01
    if maf_exac or maf_1000g or maf_esp6500:
        has_high_freq_BA1, has_high_freq_BS1 = False, False
        if maf_exac and float(maf_exac) > cutoff_BA1: has_high_freq_BA1 = True 
        if maf_1000g and float(maf_1000g) > cutoff_BA1: has_high_freq_BA1 = True 
        if maf_esp6500 and float(maf_esp6500) > cutoff_BA1: has_high_freq_BA1 = True 
        if maf_exac and float(maf_exac) > cutoff_BS1: has_high_freq_BS1 = True 
        if maf_1000g and float(maf_1000g) > cutoff_BS1: has_high_freq_BS1 = True 
        if maf_esp6500 and float(maf_esp6500) > cutoff_BS1: has_high_freq_BS1 = True 
        if has_high_freq_BA1: 
            BA1 = 1 
            curr_interpret.append('Allele frequeny is > 5%.')
            curr_interpret_chinese.append('等位基因频率 > 5%.')
        if has_high_freq_BS1: 
            BS1 = 1 
            curr_interpret.append('Allele frequeny is > 1%.')
            curr_interpret_chinese.append('等位基因频率 > 1%.')
        if not has_high_freq_BA1 and not has_high_freq_BS1:
            curr_interpret.append('Allele frequeny is <= 1%.')
            curr_interpret_chinese.append('等位基因频率 <= 1%.')
    else:
        curr_interpret.append('No allele frequency data are found in genomic databases.')
        curr_interpret_chinese.append('未在人类基因数据库中发现此等位基因的频率数据.')    
    curr_interpret.append('BA1 is met.') if BA1 == 1 else curr_interpret.append('BA1 is NOT met.')
    curr_interpret_chinese.append('符合BA1标准.') if BA1 == 1 else curr_interpret_chinese.append('不符合BA1标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('BA1 and BS1', curr_interpret))
    interpret_chinese.append(('BA1和BS1', curr_interpret_chinese))
    return BA1, BS1

def check_BA1_BS1(variant_):
    '''
    BA1 Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation Consortium
    Allele frequency is greater than expected for disorder 
    '''
    curr_interpret, curr_interpret_chinese = [], []
    maf_exac, maf_1000g, maf_esp6500 = variant_['maf_exac'], variant_['maf_1000g'], variant_['maf_esp6500']
    BA1, BS1 = 0, 0
    cutoff_BA1 = 0.05
    cutoff_BS1 = max_freq
    if maf_exac or maf_1000g or maf_esp6500:
        has_high_freq_BA1, has_high_freq_BS1 = False, False
        if maf_exac and float(maf_exac) > cutoff_BA1: has_high_freq_BA1 = True 
        if maf_1000g and float(maf_1000g) > cutoff_BA1: has_high_freq_BA1 = True 
        if maf_esp6500 and float(maf_esp6500) > cutoff_BA1: has_high_freq_BA1 = True 
        if maf_exac and cutoff_BS1 and float(maf_exac) > cutoff_BS1: has_high_freq_BS1 = True 
        if maf_1000g  and cutoff_BS1 and float(maf_1000g) > cutoff_BS1: has_high_freq_BS1 = True 
        if maf_esp6500 and cutoff_BS1 and float(maf_esp6500) > cutoff_BS1: has_high_freq_BS1 = True 
        if has_high_freq_BA1: 
            BA1 = 1 
            curr_interpret.append('Allele frequeny is > 5%.')
            curr_interpret_chinese.append('等位基因频率 > 5%.')
        if has_high_freq_BS1: 
            BS1 = 1 
            curr_interpret.append('Allele frequeny is greater than expected for disorder.')
            curr_interpret_chinese.append('等位基因频率大于由prevalence计算得到的allele frequency.')
        if not has_high_freq_BA1 and not has_high_freq_BS1:
            curr_interpret.append('Allele frequeny is smaller than expected for disorder.')
            curr_interpret_chinese.append('等位基因频率小于由prevalence计算得到的allele frequency.')
    else:
        curr_interpret.append('No allele frequency data are found in genomic databases.')
        curr_interpret_chinese.append('未在人类基因数据库中发现此等位基因的频率数据.')    
    curr_interpret.append('BA1 is met.') if BA1 == 1 else curr_interpret.append('BA1 is NOT met.')
    curr_interpret_chinese.append('符合BA1标准.') if BA1 == 1 else curr_interpret_chinese.append('不符合BA1标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('BA1 and BS1', curr_interpret))
    interpret_chinese.append(('BA1和BS1', curr_interpret_chinese))
    return BA1, BS1

def getRecessiveDominantVariants():
    global variants_recessive, variants_dominant
    variants_recessive, variants_dominant = dict(), dict()
    #maps = {'A':'T', 'T':'A', 'C':'G', 'G':'C', 'N':'N', 'X':'X'}
    with open(os.path.join(BASE, 'data/ACMG/BS2_hom_het.hg19.txt'), 'rb') as f:
        for line in f:
            line = line.rstrip()
            parts = line.split(' ')
            variant, variant_alt = parts[0], parts[1]
            variants_recessive[variant], variants_recessive[variant_alt] = parts[2], parts[2]
            variants_dominant[variant], variants_dominant[variant_alt] = parts[3], parts[3]

def check_BS2(variant_):
    '''
    Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked
    (hemizygous) disorder, with full penetrance expected at an early age
    check ExAC_ALL
    '''
    # use vcf annoation (ref, alt) from myvariant
    curr_interpret, curr_interpret_chinese = [], []
    gene, variant_ref, variant_alt, variant_id = variant_['gene'], variant_['ref'], variant_['alt'], variant_['id']
    if variant_id:
        allele_start_end_pos = re.findall(r'[0-9]{1,20}', variant_id.split('.')[-1])
    else:
        return 0
    if len(allele_start_end_pos) == 1:
        allele_start_pos = allele_end_pos = allele_start_end_pos[0]
    elif len(allele_start_end_pos) == 2:
        allele_start_pos, allele_end_pos = allele_start_end_pos
    # e.g., chr1_2068906_2068906_G_T
    variant = variant_id.split(':')[0] + '_' + allele_start_pos + '_' + allele_end_pos + '_' + variant_ref + '_' + variant_alt

    BS2 = 0
    not_adultonset_gene = True if gene not in adultonset_genes else False
    is_recessive = True if gene in recessive_genes else False
    is_homo = True if (variant in variants_recessive and variants_recessive[variant] == '1') else False
    is_dominant = True if gene in dominant_genes else False
    is_heter = True if (variant in variants_dominant and variants_dominant[variant] == '1') else False
    if not_adultonset_gene and is_recessive and is_homo: BS2 = 1
    if not_adultonset_gene and is_dominant and is_heter: BS2 = 1
    if is_recessive and is_homo: 
        curr_interpret.append('The variant is observed in a healthy adult in the 1000 Genomes Project as a homozygote (for diseases defined as recessive in OMIM).')
        curr_interpret_chinese.append('此基因变异在健康人中以隐性(纯合子)状态存在.')    
    elif is_dominant and is_heter:
        curr_interpret.append('The variant is observed in a healthy adult in the 1000 Genomes Project as a heterozygote (for diseases defined as dominant in OMIM).')
        curr_interpret_chinese.append('此基因变异在健康人中以显性(杂合子)状态存在.')
    else:
        curr_interpret.append('The variant is NOT observed in a healthy adult in the 1000 Genomes Project as a heterozygote (for dominant diseases) nor as a homozygote (for recessive diseases).')
        curr_interpret_chinese.append('此基因变异在健康人中既不以隐性(纯合子)也不以显性(杂合子)状态存在.')    
    curr_interpret.append('BS2 is met.') if BS2 == 1 else curr_interpret.append('BS2 is NOT met.')
    curr_interpret_chinese.append('符合BS2标准.') if BS2 == 1 else curr_interpret_chinese.append('不符合BS2标准.')    
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('BS2', curr_interpret))
    interpret_chinese.append(('BS2', curr_interpret_chinese))
    return BS2 

def check_BS2_bak(variant_):
    '''
    Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked
    (hemizygous) disorder, with full penetrance expected at an early age
    check ExAC_ALL
    '''
    # use vcf annoation (ref, alt) from myvariant
    curr_interpret, curr_interpret_chinese = [], []
    gene, variant_ref, variant_alt, variant_id = variant_['gene'], variant_['ref'], variant_['alt'], variant_['id']
    if variant_id:
        allele_start_end_pos = re.findall(r'[0-9]{1,20}', variant_id.split('.')[-1])
    else:
        return 0
    if len(allele_start_end_pos) == 1:
        allele_start_pos = allele_end_pos = allele_start_end_pos[0]
    elif len(allele_start_end_pos) == 2:
        allele_start_pos, allele_end_pos = allele_start_end_pos
    # e.g., chr1_2068906_2068906_G_T
    variant = variant_id.split(':')[0] + '_' + allele_start_pos + '_' + allele_end_pos + '_' + variant_ref + '_' + variant_alt

    BS2 = 0
    not_adultonset_gene = True if gene not in adultonset_genes else False
    is_recessive = True if gene in recessive_genes else False
    is_homo = True if (variant in variants_recessive and variants_recessive[variant] == '1') else False
    is_dominant = True if gene in dominant_genes else False
    is_heter = True if (variant in variants_dominant and variants_dominant[variant] == '1') else False
    if not_adultonset_gene and is_recessive and is_homo: BS2 = 1
    if not_adultonset_gene and is_dominant and is_heter: BS2 = 1
    if is_recessive and is_homo: 
        curr_interpret.append('The variant is observed in a healthy adult in the 1000 Genomes Project as a homozygote (for diseases defined as recessive in OMIM).')
        curr_interpret_chinese.append('此基因变异在健康人中以隐性(纯合子)状态存在.')    
    elif is_dominant and is_heter:
        curr_interpret.append('The variant is observed in a healthy adult in the 1000 Genomes Project as a heterozygote (for diseases defined as dominant in OMIM).')
        curr_interpret_chinese.append('此基因变异在健康人中以显性(杂合子)状态存在.')
    else:
        curr_interpret.append('The variant is NOT observed in a healthy adult in the 1000 Genomes Project as a heterozygote (for dominant diseases) nor as a homozygote (for recessive diseases).')
        curr_interpret_chinese.append('此基因变异在健康人中既不以隐性(纯合子)也不以显性(杂合子)状态存在.')    
    curr_interpret.append('BS2 is met.') if BS2 == 1 else curr_interpret.append('BS2 is NOT met.')
    curr_interpret_chinese.append('符合BS2标准.') if BS2 == 1 else curr_interpret_chinese.append('不符合BS2标准.')    
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('BS2', curr_interpret))
    interpret_chinese.append(('BS2', curr_interpret_chinese))
    return BS2 
 
   
def getBenignDomains():
    global benign_domains
    benign_domains = []
    with open(os.path.join(BASE, 'data/ACMG/PM1_domains_with_benigns.txt'), 'rb') as f:
        for line in f:
            line = line.rstrip()
            parts = line.split('\t')
            domain = 'chr' + parts[0] + '_' + parts[1] + '_' + parts[2]
            benign_domains.append(domain)

def check_PM1(variant_):
    '''
    Located in a mutational hot spot and/or critical and well-established functional domain (e.g., active site of
    an enzyme) without benign variation
    '''
    # interpro_domain can be a list
    curr_interpret, curr_interpret_chinese = [], []
    gene, variant_effect, interpro_domain, variant_id= variant_['gene'], variant_['effect'], variant_['interpro_domain'], variant_['id']
    missense_variant_types = ["missense", "rare_amino_acid_variant"]
    domains = [variant_id.split(':')[0] + '_' + gene + '_' + domain.replace('|', ';') for domain in interpro_domain]   

    PM1 = 0
    effect_in_missense_variant_types = re.search('|'.join(missense_variant_types), variant_effect, re.I)
    not_in_benign_domain = True
    for domain in domains:
        for benign_domain in benign_domains:
            if domain in benign_domain:
                not_in_benign_domain = False
                break 
    if effect_in_missense_variant_types and not_in_benign_domain: 
        PM1 = 1
        curr_interpret.append('The variant has missense effect in a critical protein domain where all missense variants in the domain identified to date have been shown to be pathogenic.')
        curr_interpret_chinese.append('此基因变异位于突变热点和/或关键的功能域(例如酶的活性部位)，且在这些区域不存在良性变异.')
    elif effect_in_missense_variant_types:
        curr_interpret.append('The variant effect is missense type but NOT in a critical protein domain where all missense variants in the domain identified to date have been shown to be pathogenic.')
        curr_interpret_chinese.append('此基因变异不位于不存在良性变异的突变热点和/或关键的功能域(例如酶的活性部位).')
    else:
        curr_interpret.append('The variant effect is NOT missense.')
        curr_interpret_chinese.append('此基因变异不是错义突变.')
    curr_interpret.append('PM1 is met.') if PM1 == 1 else curr_interpret.append('PM1 is NOT met.')
    curr_interpret_chinese.append('符合PM1标准.') if PM1 == 1 else curr_interpret_chinese.append('不符合PM1标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PM1', curr_interpret))
    interpret_chinese.append(('PM1', curr_interpret_chinese))
    return PM1 

def check_PM3_BP2():
    '''
    For recessive disorders, detected in trans with a pathogenic variant
    Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed 
    in cis with a pathogenic variant in any inheritance pattern
    '''
    PM3, BP2 = 0, 0
    return PM3, BP2

def getRepeatRegion():
    global repeat_regions 
    repeat_regions = dict()
    with open(os.path.join(BASE, 'data/ACMG/rmsk.txt'), 'rb') as f:
        for line in f:
            line = line.rstrip()
            parts = line.split('\t')
            chromosome, startpos, endpos= parts
            if chromosome in repeat_regions:
                repeat_regions[chromosome].append((int(startpos), int(endpos)))
            else:
                repeat_regions[chromosome] = [(int(startpos), int(endpos))]

def check_PM4_BP3(variant_):
    '''
    Protein length changes as a result of in-frame deletions/insertions in a nonrepeat region or stop-loss variants
    In-frame deletions/insertions in a repetitive region without a known function
    if the repetitive region is in the domain, this BP3 should not be applied.
    '''
    curr_interpret, curr_interpret_chinese = [], []
    gene, variant_effect, protein, variant_id = variant_['gene'], variant_['effect'], variant_['protein'], variant_['id']
    inframe_indel_variant_types = ["inframe_insertion", "inframe_deletion"]
    
    if not variant_id:
        return 0, 0
    chromosome = variant_id.split(':')[0]
    allele_start_end_pos = re.findall(r'[0-9]{1,20}', variant_id.split('.')[-1])
    if len(allele_start_end_pos) == 1:
        allele_start_pos = allele_end_pos = allele_start_end_pos[0]
    elif len(allele_start_end_pos) == 2:
        allele_start_pos, allele_end_pos = allele_start_end_pos
    allele_start_pos, allele_end_pos = int(allele_start_pos), int(allele_end_pos)
 
    PM4, BP3 = 0, 0
    effect_in_inframe_indel_variant_types = re.search('|'.join(inframe_indel_variant_types), variant_effect, re.I)
    repeat_region = repeat_regions[chromosome]
    in_repeat_region = False 
    for idx in xrange(len(repeat_region)):
        region = repeat_region[idx]
        if allele_end_pos < region[1]:
            if allele_start_pos >= region[0]:
                in_repeat_region = True
            break
    if effect_in_inframe_indel_variant_types and not in_repeat_region: PM4 = 1
    if effect_in_inframe_indel_variant_types and in_repeat_region: BP3 = 1

    # If the variant effect type is stop_lost, then assign 1 to PM4, no matter if the allele is in repeat/non-repeat regions
    effect_is_stop_loss = True if 'stop_lost' in variant_effect else False
    if effect_is_stop_loss: PM4 = 1
    if effect_in_inframe_indel_variant_types: 
        curr_interpret.append('Variant effect is in-frame deletions/insertion.')
        curr_interpret_chinese.append('基因变异类型是框内缺失/插入.')
    else:
        curr_interpret.append('Variant effect is NOT in-frame deletions/insertion.')
        curr_interpret_chinese.append('基因变异类型不是框内缺失/插入.')
    curr_interpret.append('Allele is in a repeat region.') if in_repeat_region else curr_interpret.append('Allele is in a nonrepeat region.')
    curr_interpret_chinese.append('变异位点在重复区域(repeat region).') if in_repeat_region else curr_interpret_chinese.append('变异位点在非重复区域(nonrepeat region).')
    if effect_is_stop_loss: 
        curr_interpret.append('Variant effect is stop loss.') 
        curr_interpret_chinese.append('基因变异类型是终止子缺失.')
    curr_interpret.append('PM4 is met.') if PM4 == 1 else curr_interpret.append('PM4 is NOT met.')
    curr_interpret_chinese.append('符合PM4标准.') if PM4 == 1 else curr_interpret_chinese.append('不符合PM4标准.')
    curr_interpret.append('BP3 is met.') if BP3 == 1 else curr_interpret.append('BP3 is NOT met.')
    curr_interpret_chinese.append('符合BP3标准.') if BP3 == 1 else curr_interpret_chinese.append('不符合BP3标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PM4 and BP3', curr_interpret))
    interpret_chinese.append(('PM4和BP3', curr_interpret_chinese))
    return PM4, BP3 

def check_PP1_BS4():
    '''
    Cosegregation with disease in multiple affected family members in a gene definitively known to cause the disease
    Lack of segregation in affected members of a family
    '''
    PP1, BS4 = 0, 0
    return PP1, BS4

def getMissenseOrTruncatePathogenicityOfGene():
    global missense_pathogenic_genes, truncate_pathogenic_genes
    missense_pathogenic_genes, trucate_pathogenic_genes = [], []
    df_missense = pd.read_csv(os.path.join(BASE, 'data/ACMG/PP2.genes.txt'), names = ['gene'])
    df_truncate = pd.read_csv(os.path.join(BASE, 'data/ACMG/BP1.genes.txt'), names = ['gene'])
    missense_pathogenic_genes = pd.unique(df_missense.gene.values).tolist()
    truncate_pathogenic_genes = pd.unique(df_truncate.gene.values).tolist()

def check_PP2_BP1(variant_):
    '''
    PP2: Missense variant in a gene that has a low rate of benign missense variation and 
    in which missense variants are a common mechanism of disease
    BP1: Missense variant in a gene for which primarily truncating variants are known to cause disease
    truncating:  stop_gain / frameshift deletion/  nonframshift deletion
    We defined Protein truncating variants as single-nucleotide variants (SNVs) predicted to introduce a premature stop codon or to disrupt a splice site, small insertions or deletions (indels) predicted to disrupt a transcript reading frame, and larger deletions 
    '''
    curr_interpret, curr_interpret_chinese = [], []
    gene, variant_effect = variant_['gene'], variant_['effect']
    missense_variant_types = ["missense", "rare_amino_acid_variant"]

    PP2, BP1 = 0, 0
    effect_in_missense_variant_types = re.search('|'.join(missense_variant_types), variant_effect, re.I)
    gene_in_missense_pathogenic_genes = True if gene in missense_pathogenic_genes else False
    gene_in_truncate_pathogenic_genes = True if gene in truncate_pathogenic_genes else False
    if effect_in_missense_variant_types and gene_in_missense_pathogenic_genes: 
        PP2 = 1
        curr_interpret.append('The missense allele is in a gene that has a low rate of benign missense variation and in which missense variants are a common mechanism of disease.')
        curr_interpret_chinese.append('此错义突变发生在这样一个基因上：良性错义突变在这个基因上的频率低，且在这个基因上的错义突变是致病的常见原因.')
    if effect_in_missense_variant_types and gene_in_truncate_pathogenic_genes: 
        BP1 = 1
        curr_interpret.append('The missense allele is in a gene for which primarily truncating variants are known to cause disease.')
        curr_interpret_chinese.append('错义突变位于截短(truncating)变异是致病主要原因的基因上.')    
    if not effect_in_missense_variant_types:
        curr_interpret.append('The variant effect is NOT missense.')
        curr_interpret_chinese.append('此基因变异类型不是错义突变.')
    elif not gene_in_missense_pathogenic_genes and not gene_in_truncate_pathogenic_genes:
        curr_interpret.append('The variant effect is missense, but neither in a gene that has a low rate of benign missense variation and in which missense variants are a common mechanism of disease nor in a gene for which primarily truncating variants are known to cause disease.')
        curr_interpret_chinese.append('此基因变异类型是错义突变，但并非发生在以下两种类型的基因上：(1) 良性错义突变在基因上的频率低，且在这个基因上的错义突变是致病的常见原因；(2) 基因的截短(truncating)变异是致病的主要原因.')
    curr_interpret.append('PP2 is met.') if PP2 == 1 else curr_interpret.append('PP2 is NOT met.')
    curr_interpret_chinese.append('符合PP2标准.') if PP2 == 1 else curr_interpret_chinese.append('不符合PP2标准.')
    curr_interpret.append('BP1 is met.') if BP1 == 1 else curr_interpret.append('BP1 is NOT met.')
    curr_interpret_chinese.append('符合BP1标准.') if BP1 == 1 else curr_interpret_chinese.append('不符合BP1标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PP2 and BP1', curr_interpret))
    interpret_chinese.append(('PP2和BP1', curr_interpret_chinese))
    return PP2, BP1

def evalPathogenicityScore(algo_score, key):
    cutoff = {'dann':0.96, 'fathmm':0.81415, 'metasvm':0.83357, 'gerp++':2.0, 'dbscSNV_rf_score':0.6, 'dbscSNV_ada_score':0.6}
    is_pathogenic = 'N/A'
    if algo_score:
        if float(algo_score) > cutoff[key]:
            is_pathogenic = 'D' 
        else:
            is_pathogenic = 'N' 
    return is_pathogenic 

def check_PP3_BP4(variant_):
    '''
    PP3: Multiple lines of computational evidence support a deleterious effect on the gene or gene product
    (conservation, evolutionary, splicing impact, etc.)
    sfit for conservation, GERP++_RS for evolutionary, splicing impact from dbNSFP
    BP4: Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, 
    evolutionary,splicing impact, etc.)
    '''
    curr_interpret, curr_interpret_chinese = [], []
    dann, fathmm, metasvm, gerp = variant_['dann'], variant_['fathmm'], variant_['metasvm'], variant_['gerp++']
    dbscSNV_rf_score, dbscSNV_ada_score = variant_['dbscSNV_rf_score'], variant_['dbscSNV_ada_score']

    PP3, BP4 = 0, 0 
    cutoff = {'dann':0.96, 'fathmm':0.81415, 'metasvm':0.83357, 'gerp++':2.0, 'dbscSNV_rf_score':0.6, 'dbscSNV_ada_score':0.6}
    is_pathogenic_dann = evalPathogenicityScore(dann, 'dann') 
    is_pathogenic_fathmm = evalPathogenicityScore(fathmm, 'fathmm') 
    is_pathogenic_metasvm = evalPathogenicityScore(metasvm, 'metasvm') 
    is_pathogenic_gerp = evalPathogenicityScore(gerp, 'gerp++')
    # print dbscSNV_rf_score, dbscSNV_ada_score
    if (dbscSNV_rf_score and float(dbscSNV_rf_score) > cutoff['dbscSNV_rf_score']) or (dbscSNV_ada_score and float(dbscSNV_ada_score) > cutoff['dbscSNV_ada_score']):
        is_pathogenic_dbscSNV = 'D'
    elif (not dbscSNV_rf_score) and (not dbscSNV_ada_score):
        is_pathogenic_dbscSNV = 'N/A'
    else:
        is_pathogenic_dbscSNV = 'N' # if dbscSNV scores are missing, the allele is not in the splice sequence, should be benign
    is_pathogenic = [is_pathogenic_dann, is_pathogenic_fathmm, is_pathogenic_metasvm, is_pathogenic_gerp, is_pathogenic_dbscSNV] 
    # print is_pathogenic
    try:
        PP3 = float(is_pathogenic.count('D')) / (is_pathogenic.count('D') + is_pathogenic.count('N'))
    except ZeroDivisionError:
        PP3 = 0
    #if 'N' in is_pathogenic: PP3 = 0
    if 'N' in is_pathogenic and 'D' not in is_pathogenic: BP4 = 1 
    curr_interpret.append('The cutoffs for computational pathogenicity predictions are %s.' % ('DANN:0.96, FATHMM:0.81415, MetaSVM:0.83357, GERP++:2.0, dbscSNV_rf_score:0.6, dbscSNV_ada_score:0.6'))
    curr_interpret_chinese.append('各致病性算法的致病分数阈值是：%s.' % ('DANN:0.96, FATHMM:0.81415, MetaSVM:0.83357, GERP++:2.0, dbscSNV_rf_score:0.6, dbscSNV_ada_score:0.6'))    
    if PP3 == 1:
        curr_interpret.append('PP3 is met.')
        curr_interpret_chinese.append('符合PP3标准.') 
    elif PP3 == 0:
        curr_interpret.append('PP3 is NOT met.')
        curr_interpret_chinese.append('不符合PP3标准.')
    else:
        curr_interpret.append('PP3 is partially met.')
        curr_interpret_chinese.append('部分符合PP3标准(部分致病性算法预测此变异致病).')
    curr_interpret.append('BP4 is met.') if BP4 == 1 else curr_interpret.append('BP4 is NOT met.')
    curr_interpret_chinese.append('符合BP4标准.') if BP4 == 1 else curr_interpret_chinese.append('不符合BP4标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PP3 and BP4', curr_interpret))
    interpret_chinese.append(('PP3和BP4', curr_interpret_chinese))
    return PP3, BP4

def getTopRankedGenes(df_hpo_ranking_genes):
    global top_ranked_genes
    num_genes = df_hpo_ranking_genes.shape[0]
    num = int(num_genes * 0.1)
    df_top_ranked_genes = df_hpo_ranking_genes[0:num]
    top_ranked_genes = pd.unique(df_top_ranked_genes.gene.values).tolist()

def check_PP4(variant_, gene_associated_phenos):
    '''
    Patient's phenotype or family history is highly specific for a disease with a single genetic etiology
    '''
    curr_interpret, curr_interpret_chinese = [], []
    gene = variant_['gene']
    PP4 = 0
    if not gene_associated_phenos:
        interpret.append(('PP4', 'No phenotypes are provided. PP4 is not met.'))
        interpret_chinese.append(('PP4', '未提供表型信息. 不满足PP4标准.'))
        return PP4
    if gene not in gene_associated_phenos or not gene_associated_phenos[gene]:
        interpret.append(('PP4', 'No phenotypes are associated. PP4 is not met.'))
        interpret_chinese.append(('PP4', '病人无与此基因相关的表型. 不满足PP4标准.'))
    else:
        matched_phenos = gene_associated_phenos[gene]
        if gene in top_ranked_genes:
            PP4 = 1
            interpret.append(('PP4', "The following phenotypes are associated: %s. And the gene is among the top ranked genes that associate with patient's phenotypes. PP4 is met." % matched_phenos))     
            interpret_chinese.append(('PP4', "病人的下述表型与当前基因相关: %s. 而且当前基因与此病人的表型匹配得分在此病人的所有突变中排名靠前. 满足PP4标准." % matched_phenos))     
        else:
            interpret.append(('PP4', "The following phenotypes are associated: %s. But the gene is not among the top ranked genes that associate with patient's phenotypes. PP4 is not met." % matched_phenos))     
            interpret_chinese.append(('PP4', "病人的下述表型与当前基因相关: %s. 但是当前基因与此病人的表型匹配得分在此病人的所有突变中排名不靠前. 不满足PP4标准." % matched_phenos))     
    return PP4

def check_PP5_BP6(variant_):
    '''
    PP5: Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory
    to perform an independent evaluation
    BP6: Reputable source recently reports variant as benign, but the evidence is not available to the 
    laboratory to perform an independent evaluation; Check the ClinVar column to see whether this 
    is "benign". 
    '''
    curr_interpret, curr_interpret_chinese = [], []
    clinvar_pathogenicity = variant_['clinvar_pathogenicity']
    clinvar_pmids, clinvar_variation_ids, clinvar_review_status = variant_['clinvar_pmids'], variant_['clinvar_variation_ids'], variant_['clinvar_review_status']   
    clinvar_pmids = ["<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'> %s </a>" %(i,i) for i in clinvar_pmids]
    clinvar_variation_ids = ["<a href='https://www.ncbi.nlm.nih.gov/clinvar/variation/%s/'> %s </a>" %(i,i) for i in clinvar_variation_ids.split('|')]
    # clinvar_pmids is a list
    clinvar_variation_ids = ', '.join(clinvar_variation_ids)
    if clinvar_review_status:
        clinvar_review_status = clinvar_review_status.split('|')
        reviewstatusmap = {'no assertion criteria provided':0.5, 'no assertion provided':0.5, 'no assertion for the individual variant':0.5, 'criteria provided, single submitter':1, 'criteria provided, conflicting interpretations':0.75, 'criteria provided, multiple submitters, no conflicts':1.5, 'reviewed by expert panel':2, 'practice guideline':2.5} 
        clinvar_review_status = [reviewstatusmap[review] for review in clinvar_review_status]
        clinvar_review_status = max(clinvar_review_status)
    else:
        clinvar_review_status = 1.0
 
    PP5, BP6 = 0, 0
    pathogenic_keywords = ['pathogenic', 'risk factor']
 
    expert_submitters = ['genedx', 'invitae', 'laboratory for molecular medicine']
    pathogenicity_score = {'pathogenic':1.0, 'likely pathogenic':0.5, 'risk factor': 0.5, 'uncertain significance':0.0, 'likely benign':-0.5, 'benign':-1.0}
    total_pathogenicity_score, num_clinical_records = 0.0, 0 
    clinvar_pathogenicity_, clinvar_comments = [], []
    for record in clinvar_pathogenicity:
        description, submitter, datelastevaluated, method, comment = record
        if re.search(r'literature', method, re.I) or re.search(r'not provided', description, re.I):
            continue
        clinvar_pathogenicity_.append(description.lower())
        num_clinical_records += 1
        score = 1.0
        for expert_submitter in expert_submitters:
            if submitter.lower().startswith(expert_submitter):
                score = score * 2.0
                if comment:
                    clinvar_comments.append(comment)
                break
        if description.lower() in pathogenicity_score.keys():
            score = score * pathogenicity_score[description.lower()]
        else:
            score = score * 0.0
        if datelastevaluated >= '2017-01-01':
            score = score * 2.0
        elif datelastevaluated >= '2015-01-01':
            score = score * 1.5 
        elif datelastevaluated >= '2010-01-01':
            score = score * 1.25
        else:
            score = score * 1.0
        total_pathogenicity_score += score
    if num_clinical_records != 0:
        total_pathogenicity_score = total_pathogenicity_score / num_clinical_records
    else:
        total_pathogenicity_score = 0.0
    clinvar_pathogenicity_ = '|'.join(clinvar_pathogenicity_)
    clinvar_comments = ' '.join(clinvar_comments)

    if ('pathogenic' in clinvar_pathogenicity_ or 'risk factor' in clinvar_pathogenicity_) and 'benign' not in clinvar_pathogenicity_ and 'conflicting' not in clinvar_pathogenicity_:
        PP5 = total_pathogenicity_score * clinvar_review_status
        curr_interpret.append('Clinvar (clinical testing records) reports the variant as pathogenic (Clinvar: %s).' % clinvar_variation_ids)
        curr_interpret_chinese.append('Clinvar (临床试验(clinical testing)记录) 报道此基因变异致病(Clinvar IDs: %s).' % clinvar_variation_ids)
        if clinvar_pmids:
            curr_interpret.append('Pubmed references: %s.' % ', '.join(clinvar_pmids))
            curr_interpret_chinese.append('生物医学参考文献Pubmed: %s.' % ', '.join(clinvar_pmids))
        if clinvar_comments:
            curr_interpret.append('Summary evidence: %s.' % clinvar_comments)
            curr_interpret_chinese.append('简要证据: %s.' % clinvar_comments)
    elif ('benign' in clinvar_pathogenicity_ or 'protective' in clinvar_pathogenicity_) and 'pathogenic' not in clinvar_pathogenicity_ and 'conflicting' not in clinvar_pathogenicity_:
        BP6 = total_pathogenicity_score * clinvar_review_status
        curr_interpret.append('Clinvar (clinical testing records)  reports the variant as benign (Clinvar: %s).' % clinvar_variation_ids)
        curr_interpret_chinese.append('Clinvar (临床试验(clinical testing)记录) 报道此基因变异良性(Clinvar IDs: %s).' % clinvar_variation_ids)
        if clinvar_pmids:
            curr_interpret.append('Pubmed references: %s.' % ', '.join(clinvar_pmids))
            curr_interpret_chinese.append('生物医学参考文献Pubmed: %s.' % ', '.join(clinvar_pmids))    
        if clinvar_comments:
            curr_interpret.append('Summary evidence: %s.' % clinvar_comments)
            curr_interpret_chinese.append('简要证据: %s.' % clinvar_comments)
    elif clinvar_pathogenicity_:
        curr_interpret.append('Clinvar (clinical testing records)  does NOT have a conclusion on this variant (Clinvar: %s).' % clinvar_variation_ids)
        curr_interpret_chinese.append('Clinvar数据库 (临床试验(clinical testing)记录) 中关于此基因变异的致病性没有确定的结论(Clinvar IDs: %s).' % clinvar_variation_ids)
        if clinvar_comments:
            curr_interpret.append('Summary evidence: %s.' % clinvar_comments)
            curr_interpret_chinese.append('简要证据: %s.' % clinvar_comments)
    else:
        curr_interpret.append('Clinvar (clinical testing records)  does NOT have records on this variant.')
        curr_interpret_chinese.append('未在Clinvar数据库 (临床试验(clinical testing)记录) 中发现关于此基因变异致病性的报道.')
        #if clinvar_comments:
        #    curr_interpret.append('Summary evidence: %s.' % clinvar_comments)
        #    curr_interpret_chinese.append('简要证据: %s.' % clinvar_comments)

    curr_interpret.append('PP5 is met.') if PP5 != 0 else curr_interpret.append('PP5 is NOT met.')
    curr_interpret_chinese.append('符合PP5标准.') if PP5 != 0 else curr_interpret_chinese.append('不符合PP5标准.')
    curr_interpret.append('BP6 is met.') if BP6 != 0 else curr_interpret.append('BP6 is NOT met.')
    curr_interpret_chinese.append('符合BP6标准.') if BP6 != 0 else curr_interpret_chinese.append('不符合BP6标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PP5 and BP6', curr_interpret))
    interpret_chinese.append(('PP5和BP6', curr_interpret_chinese))
    return PP5, BP6

def check_PP5_BP6_bak(variant_):
    '''
    PP5: Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory
    to perform an independent evaluation
    BP6: Reputable source recently reports variant as benign, but the evidence is not available to the 
    laboratory to perform an independent evaluation; Check the ClinVar column to see whether this 
    is "benign". 
    '''
    curr_interpret, curr_interpret_chinese = [], []
    clinvar_pathogenicity = variant_['clinvar_pathogenicity'].lower()
    clinvar_pmids, clinvar_variation_ids, clinvar_review_status = variant_['clinvar_pmids'], variant_['clinvar_variation_ids'], variant_['clinvar_review_status']   
    clinvar_pmids = ["<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'> %s </a>" %(i,i) for i in clinvar_pmids]
    clinvar_variation_ids = ["<a href='https://www.ncbi.nlm.nih.gov/clinvar/variation/%s/'> %s </a>" %(i,i) for i in clinvar_variation_ids.split('|')]
    # clinvar_pmids is a list
    clinvar_variation_ids = ', '.join(clinvar_variation_ids)
    if clinvar_review_status:
        clinvar_review_status = clinvar_review_status.split('|')
        reviewstatusmap = {'no assertion criteria provided':0.5, 'no assertion provided':0.5, 'no assertion for the individual variant':0.5, 'criteria provided, single submitter':1, 'criteria provided, conflicting interpretations':0.75, 'criteria provided, multiple submitters, no conflicts':1.5, 'reviewed by expert panel':2, 'practice guideline':2.5} 
        clinvar_review_status = [reviewstatusmap[review] for review in clinvar_review_status]
        clinvar_review_status = max(clinvar_review_status)
    else:
        clinvar_review_status = 1.0
 
    PP5, BP6 = 0, 0
    pathogenic_keywords = ['pathogenic', 'risk factor']
    if ('pathogenic' in clinvar_pathogenicity or 'risk factor' in clinvar_pathogenicity) and 'benign' not in clinvar_pathogenicity and 'conflicting' not in clinvar_pathogenicity:
        PP5 = 1 * clinvar_review_status
        curr_interpret.append('Clinvar reports the variant as pathogenic (Clinvar: %s).' % clinvar_variation_ids)
        curr_interpret_chinese.append('Clinvar报道此基因变异致病(Clinvar IDs: %s).' % clinvar_variation_ids)
        if clinvar_pmids:
            curr_interpret.append('Pubmed references: %s.' % ', '.join(clinvar_pmids))
    elif ('benign' in clinvar_pathogenicity or 'protective' in clinvar_pathogenicity) and 'pathogenic' not in clinvar_pathogenicity and 'conflicting' not in clinvar_pathogenicity:
        BP6 = 1 * clinvar_review_status
        curr_interpret.append('Clinvar reports the variant as benign (Clinvar: %s).' % clinvar_variation_ids)
        curr_interpret_chinese.append('Clinvar报道此基因变异良性(Clinvar IDs: %s).' % clinvar_variation_ids)
        if clinvar_pmids:
            curr_interpret.append('Pubmed references: %s.' % ', '.join(clinvar_pmids))
            curr_interpret_chinese.append('生物医学参考文献Pubmed: %s.' % ', '.join(clinvar_pmids))    
    elif clinvar_pathogenicity:
        curr_interpret.append('Clinvar does NOT have a conclusion on this variant (Clinvar: %s).' % clinvar_variation_ids)
        curr_interpret_chinese.append('未在数据库中发现关于此基因变异致病性的一致性结论(Clinvar IDs: %s).' % clinvar_variation_ids)
    else:
        curr_interpret.append('Clinvar does NOT have records on this variant.')
        curr_interpret_chinese.append('未在数据库中发现关于此基因变异致病性的报道.')

    curr_interpret.append('PP5 is met.') if PP5 != 0 else curr_interpret.append('PP5 is NOT met.')
    curr_interpret_chinese.append('符合PP5标准.') if PP5 != 0 else curr_interpret_chinese.append('不符合PP5标准.')
    curr_interpret.append('BP6 is met.') if BP6 != 0 else curr_interpret.append('BP6 is NOT met.')
    curr_interpret_chinese.append('符合BP6标准.') if BP6 != 0 else curr_interpret_chinese.append('不符合BP6标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('PP5 and BP6', curr_interpret))
    interpret_chinese.append(('PP5和BP6', curr_interpret_chinese))
    return PP5, BP6

def check_BP5():
    '''
    Variant found in a case with an alternate molecular basis for disease
    check the genes whether are for mutilfactor disorder
    The reviewers suggeset to disable the OMIM morbidmap for BP5
    '''
    BP5 = 0
    return BP5

def check_BP7(variant_):
    '''
    A synonymous (silent) variant for which splicing prediction algorithms predict no impact to the 
    splice consensus sequence nor the creation of a new splice site AND the nucleotide is not highly 
    conserved
    '''
    curr_interpret, curr_interpret_chinese = [], []
    variant_effect = variant_['effect']
    gerp = variant_['gerp++']
    dbscSNV_rf_score, dbscSNV_ada_score = variant_['dbscSNV_rf_score'], variant_['dbscSNV_ada_score']
    synonymous_variant_types = ["synonymous", "start_retained", "stop_retained"]

    BP7 = 0
    conserv_cutoff = 2 # for GERP++
    dbscSNV_cutoff = 0.6
    effect_in_synonymous_variant_types = re.search('|'.join(synonymous_variant_types), variant_effect, re.I)
    not_affect_splicing = False if ((dbscSNV_rf_score and float(dbscSNV_rf_score) > dbscSNV_cutoff) or (dbscSNV_ada_score and float(dbscSNV_ada_score) > dbscSNV_cutoff)) else True 
    is_conservative = True if (gerp and float(gerp) > conserv_cutoff) else False
    if effect_in_synonymous_variant_types and not_affect_splicing and not is_conservative: BP7 = 1
    if BP7 == 1: 
        curr_interpret.append('Variant effect is synonymous (silent) for which splicing prediction algorithms predict no impact to the splice consensus sequence nor the creation of a new splice site AND the nucleotide is not highly conserved.')
        curr_interpret_chinese.append('变异类型为同义（沉默）变异，剪接预测算法预测此变异对剪接序列没有影响，核苷酸不是高度保守的.')
    elif effect_in_synonymous_variant_types and is_conservative:
        curr_interpret.append('Variant effect is synonymous (silent) but the nucleotide is highly conserved.')
        curr_interpret_chinese.append('变异类型为同义（沉默）变异，但核苷酸序列高度保守.')
    elif effect_in_synonymous_variant_types and not not_affect_splicing:
        curr_interpret.append('Variant effect is synonymous (silent) but the splicing prediction algorithms predict impact to the splice consensus sequence.')
        curr_interpret_chinese.append('变异类型为同义（沉默）变异，剪接预测算法预测此变异影响剪接序列.')
    elif effect_in_synonymous_variant_types:
        curr_interpret.append('Variant effect is synonymous (silent).')
        curr_interpret_chinese.append('变异类型为同义（沉默）变异.')
    else:
        curr_interpret.append('Variant effect is not synonymous.')
        curr_interpret_chinese.append('变异类型非同义（沉默）变异.')

    curr_interpret.append('BP7 is met.') if BP7 == 1 else curr_interpret.append('BP7 is NOT met.')
    curr_interpret_chinese.append('符合BP7标准.') if BP7 == 1 else curr_interpret_chinese.append('不符合BP7标准.')
    curr_interpret = ' '.join(curr_interpret)
    curr_interpret_chinese = ' '.join(curr_interpret_chinese)
    interpret.append(('BP7', curr_interpret))
    interpret_chinese.append(('BP7', curr_interpret_chinese))
    return BP7

def queryPubmedDB(pmids_from_clinvar):
    db = MySQLdb.connect(host="127.0.0.1",
                     user="root",
                     passwd="Tianqi12",
                     db="DB_offline")
    pubmed_articles_from_clinvar = dict() 
    if not pmids_from_clinvar:
        return pubmed_articles_from_clinvar
    query = "select distinct pmid, title, journal, year, impact_factor, pathogenicity_score from pubmed_var where pmid in (%s)" % (', '.join(pmids_from_clinvar))
    #print '++++++++++++++++++++++++++++++++++++++++++'
    #print pmids_from_clinvar
    #print query
    cursor = db.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    #print data
    for line in data:
        pmid, title, journal, year, impact_factor, pathogenicity_score = line
        pubmed_articles_from_clinvar[pmid] = (title, journal, year, impact_factor, pathogenicity_score)
    return pubmed_articles_from_clinvar

def getWeight(criteria):
    if re.match('PVS', criteria): return 3.0
    if re.match('PS', criteria): return 2.0
    if re.match('PM', criteria): return 1.0
    if re.match('PP', criteria): return 0.5
    if re.match('BA', criteria): return -3.0 
    if re.match('BS', criteria): return -2.0 
    if re.match('BP', criteria): return -0.5 

def classify(ACMG_score_list):
    PVS1, PS1, PS2, PS3, PS4, PM1, PM2, PM3, PM4, PM5, PM6, PP1, PP2, PP3, PP4, PP5, BA1, BS1, BS2, BS3, BS4, BP1, BP2, BP3, BP4, BP5, BP6, BP7 = ACMG_score_list
    ACMG_criteria_list = ['PVS1', 'PS1', 'PS2', 'PS3', 'PS4', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5', 'PM6', 'PP1', 'PP2', 'PP3', 'PP4', 'PP5', 'BA1', 'BS1', 'BS2', 'BS3', 'BS4', 'BP1', 'BP2', 'BP3', 'BP4', 'BP5', 'BP6', 'BP7']
    ACMG_score = dict(zip(ACMG_criteria_list, ACMG_score_list)) 
    # print ACMG_score
    ACMG_weighted_score = 0 
    hit_criteria = []
    for criteria in ACMG_score.keys():
        score = ACMG_score[criteria] 
        weight = getWeight(criteria)
        # print criteria
        # print 'score', score 
        # print 'weight', weight
        score = score * weight
        ACMG_weighted_score += score
        if score: hit_criteria.append(criteria)

    PS = PS1 + PS2 + PS3 + PS4 
    PM = PM1 + PM2 + PM3 + PM4 + PM5 + PM6
    PP = PP1 + PP2 + PP3 + PP4 + PP5 
    BS = BS1 + BS2 + BS3 + BS4
    BP = BP1 + BP2 + BP3 + BP4 + BP5 + BP6 + BP7
    classification = [] 
    if PVS1 and (PS >= 1 or PM >= 2 or (PM == 1 and PP == 1) or PP >= 2): classification.append('Pathogenic')
    if PS >= 2: classification.append('Pathogenic')
    if PS >= 1 and (PM >= 3 or (PM >= 2 and PP >= 2) or (PM >= 1 and PP >= 4)): classification.append('Pathogenic')
    if (PVS1 and PM == 1) or (PS == 1 and (PM == 1 or PM == 2)): classification.append('Likely pathogenic')
    if (PS == 1 and PP >= 2) or (PM >= 3): classification.append('Likely pathogenic')
    if (PM == 2 and PP >= 2) or (PM == 1 and PP >= 4): classification.append('Likely pathogenic')
    if (BA1 == 1) or (BS >= 2): classification.append('Benign')
    if (BS == 1 and BP == 1) or (BP >= 2): classification.append('Likely benign')
    joined_classification = '|'.join(classification)
    is_pathogenic = re.search('pathogenic', joined_classification, re.I)
    is_benign = re.search('benign', joined_classification, re.I)
    if is_pathogenic and not is_benign:
        if 'Pathogenic' in classification:
            return 'Pathogenic', ACMG_weighted_score, '|'.join(hit_criteria)
        else:
            return 'Likely pathogenic', ACMG_weighted_score, '|'.join(hit_criteria)
    if is_benign and not is_pathogenic:
        if 'Benign' in classification:
            return 'Benign', ACMG_weighted_score, '|'.join(hit_criteria)
        else:
            return 'Likely benign', ACMG_weighted_score, '|'.join(hit_criteria)
    return 'Uncertain significance', ACMG_weighted_score, '|'.join(hit_criteria)

def getDisease2OMIMID():
    global disease2omimid
    infile = open(os.path.join(BASE, 'data/disease2omimid.p'), 'rb')
    disease2omimid = pickle.load(infile)
    infile.close() 

def getOMIM2GeneReviewsName():
    global omim_gene_reviews_name
    infile = open(os.path.join(BASE, 'data/omim_genereviews.p'), 'rb')
    omim_gene_reviews_name = pickle.load(infile)
    infile.close() 

def getDiseasePenetrance():
    global complete_penetrance_gr_shortnames, incomplete_penetrance_gr_shortnames
    infile = open(os.path.join(BASE, 'data/gr_shortname_penetrance_lists.p'), 'rb')
    complete_penetrance_gr_shortnames, incomplete_penetrance_gr_shortnames = pickle.load(infile)
    infile.close()

def adjustPM3andBP2(variants, variant_ACMG_result, variant_ACMG_weighted_score, variant_ACMG_hit_criteria, variant_ACMG_score, variant_ACMG_interpret, variant_ACMG_interpret_chinese):
    '''
    For recessive disorders, detected in trans with a pathogenic variant
    Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed 
    in cis with a pathogenic variant in any inheritance pattern
    '''
    variants_need_to_be_adjusted = []
    for key in variant_ACMG_result.keys():
        gene, variant = key
        classification_result = variant_ACMG_result[key]  
        zygosity = variants[key]['zygosity']
        clinvar_diseases = variants[key]['clinvar_associated_diseases']
        disease_is_dominant, disease_is_recessive = False, False
        disease_is_complete_penetrant = False
        clinvar_diseases = clinvar_diseases.split('|')
        for disease in clinvar_diseases:
            disease = disease.lower()
            if disease in dominant_diseases:
                disease_is_dominant = True
                try:
                    gr_shortname = omim_gene_reviews_name[disease2omimid[disease]]
                    if gr_shortname in complete_penetrance_gr_shortnames:
                        disease_is_complete_penetrant = True
                except:
                    pass
            if disease in recessive_diseases:
                disease_is_recessive = True

        PM3, BP2 = 0, 0
        if disease_is_recessive and re.match(r'comp', zygosity, re.I) and classification_result in ['Pathogenic', 'Likely pathogenic']:
            for key2 in variant_ACMG_result.keys():
                gene2, variant2 = key2
                if gene == gene2 and variant != variant2:
                    ACMG_score_list = variant_ACMG_score[key2]
                    PM3 = 1 if classification_result == 'Pathogenic' else 0.5
                    ACMG_score_list[7] = PM3
                    variant_ACMG_score[key2] = ACMG_score_list
                    variants_need_to_be_adjusted.append(key2)

        if disease_is_dominant and not disease_is_recessive and re.match(r'comp', zygosity, re.I) and classification_result in ['Pathogenic', 'Likely pathogenic'] and disease_is_complete_penetrant: 
            for key2 in variant_ACMG_result.keys():
                gene2, variant2 = key2
                if gene == gene2 and variant != variant2:
                    ACMG_score_list = variant_ACMG_score[key2]
                    BP2 = 1 if classification_result == 'Pathogenic' else 0.5 
                    ACMG_score_list[22] = BP2 
                    variant_ACMG_score[key2] = ACMG_score_list
                    variants_need_to_be_adjusted.append(key2)

        if classification_result in ['Pathogenic', 'Likely pathogenic']: 
            for key2 in variant_ACMG_result.keys():
                gene2, variant2 = key2
                if gene == gene2 and variant != variant2:
                    zygosity2 = variants[key2]['zygosity']
                    if not re.match(r'comp', zygosity2, re.I):
                        ACMG_score_list = variant_ACMG_score[key2]
                        BP2 = 1 if classification_result == 'Pathogenic' else 0.5 
                        ACMG_score_list[22] = BP2 
                        variant_ACMG_score[key2] = ACMG_score_list
                        variants_need_to_be_adjusted.append(key2)

    for key in variants_need_to_be_adjusted:
        curr_interpret, curr_interpret_chinese = [], []
        PM3, BP2 = variant_ACMG_score[key][7], variant_ACMG_score[key][22] 
    	classification_result, ACMG_weighted_score, hit_criteria = classify(variant_ACMG_score[key]) 
    	variant_ACMG_result[key] = classification_result
    	variant_ACMG_weighted_score[key] = ACMG_weighted_score 
    	variant_ACMG_hit_criteria[key] = hit_criteria
        if PM3 > 0:
            curr_interpret.append('For recessive disorders, detected in trans with a pathogenic variant. PM3 is met.')
            curr_interpret_chinese.append('For recessive disorders, detected in trans with a pathogenic variant. PM3 is met.')
        if BP2 > 0:
            curr_interpret.append('Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in cis with a pathogenic variant in any inheritance pattern. BP2 is met.')
            curr_interpret_chinese.append('Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in cis with a pathogenic variant in any inheritance pattern. BP2 is met.')
        curr_interpret = ' '.join(curr_interpret)
        curr_interpret_chinese = ' '.join(curr_interpret_chinese)
        interpret.append(('PM3 and BP2', curr_interpret))
        interpret_chinese.append(('PM3 and BP2', curr_interpret_chinese))
    	variant_ACMG_interpret[key].append(('PM3 and BP2', curr_interpret))
    	variant_ACMG_interpret_chinese[key].append(('PM3 and BP2', curr_interpret_chinese))
    return variant_ACMG_score, variant_ACMG_result, variant_ACMG_weighted_score, variant_ACMG_hit_criteria, variant_ACMG_interpret, variant_ACMG_interpret_chinese

def getGene2OMIM():
    global gene2omim
    df_gene2mim = pd.read_csv(os.path.join(BASE, 'data/ACMG/mim2gene.txt'), sep = '\t', skiprows = 5, usecols = [0, 1, 3], names = ['mim', 'type', 'gene'])
    df_gene2mim = df_gene2mim.loc[df_gene2mim['type'] == 'gene', ['mim', 'gene']]
    gene2omim = df_gene2mim.set_index('gene')['mim'].to_dict()

def Get_ACMG_result(df_hpo_ranking_genes, variants, df_pubmed, parent_ngs, parent_affects, gene_associated_phenos, df_pubmed_genes_novariant):
    global interpret, curr_interpret, interpret_chinese, curr_interpret_chinese, pubmed_articles

    map_clinvar_pathogenicity = {'Uncertain significance':'意义不明确', 'Likely benign':'可能良性', 'Pathogenic':'致病', 'Benign':'良性', 'Likely pathogenic':'可能致病', 'pathologic': '致病', 'not provided':'未提供结论', 'Conflicting interpretations of pathogenicity':'致病性结论不一致', 'other':'其它', 'risk factor':'风险因子', 'drug response':'药物反应', 'Conflicting interpretations of pathogenicity, not provided':'致病性结论不一致', 'Benign/Likely benign':'良性/可能良性', 'association':'有关联', 'conflicting data from submitters':'致病性结论不一致', 'protective':'保护作用', 'Pathogenic, risk factor':'致病，风险因子', 'Pathogenic/Likely pathogenic':'致病、可能致病', 'Likely pathogenic, risk factor':'可能致病，风险因子', 'Pathogenic, other':'致病', 'Likely benign, protective':'可能良性，保护作用', 'Conflicting interpretations of pathogenicity, risk factor':'致病性结论不一致', 'Benign, other':'良性', 'Uncertain significance, risk factor':'意义不明确，风险因子', 'Pathogenic, association':'致病', 'Likely benign, risk factor':'可能良性，风险因子', 'Benign, risk factor':'良性，风险因子', 'Uncertain significance, other':'意义不明确', 'Uncertain significance, Affects':'意义不明确', 'Pathogenic, Affects':'致病', 'Conflicting interpretations of pathogenicity, other':'致病性结论不一致', 'Conflicting interpretations of pathogenicity, Affects':'致病性结论不一致', 'confers sensitivity':'提高灵敏度'}
    map_clinvar_pathogenicity = {'uncertain significance':'意义不明确', 'likely benign':'可能良性', 'pathogenic':'致病', 'benign':'良性', 'likely pathogenic':'可能致病', 'pathologic': '致病', 'not provided':'未提供结论', 'conflicting interpretations of pathogenicity':'致病性结论不一致', 'other':'其它', 'risk factor':'风险因子', 'drug response':'药物反应', 'conflicting interpretations of pathogenicity, not provided':'致病性结论不一致', 'benign/likely benign':'良性/可能良性', 'association':'有关联', 'conflicting data from submitters':'致病性结论不一致', 'protective':'保护作用', 'pathogenic, risk factor':'致病，风险因子', 'pathogenic/likely pathogenic':'致病、可能致病', 'likely pathogenic, risk factor':'可能致病，风险因子', 'pathogenic, other':'致病', 'likely benign, protective':'可能良性，保护作用', 'conflicting interpretations of pathogenicity, risk factor':'致病性结论不一致', 'benign, other':'良性', 'uncertain significance, risk factor':'意义不明确，风险因子', 'pathogenic, association':'致病', 'likely benign, risk factor':'可能良性，风险因子', 'benign, risk factor':'良性，风险因子', 'uncertain significance, other':'意义不明确', 'uncertain significance, affects':'意义不明确', 'pathogenic, affects':'致病', 'conflicting interpretations of pathogenicity, other':'致病性结论不一致', 'conflicting interpretations of pathogenicity, affects':'致病性结论不一致', 'confers sensitivity':'提高灵敏度'}
    map_clinvar_review_status = {'criteria provided, single submitter':'提供标准，单个提交者', 'no assertion criteria provided':'未提供标准', 'no assertion provided':'未提供结论', 'criteria provided, multiple submitters, no conflicts':'提供标准，多个提交者，致病性结论一致', 'criteria provided, conflicting interpretations':'提供标准，致病性结论不一致', 'reviewed by expert panel':'通过专家评审', 'practice guideline':'实践指南'}
    map_clinvar_pathogenicity_keys = [key for key in map_clinvar_pathogenicity.keys()]
    map_clinvar_pathogenicity_keys.sort(key=len, reverse=True)
    map_clinvar_review_status_keys = map_clinvar_review_status.keys()
    map_clinvar_review_status_keys.sort(key=len, reverse=True)
    re_map_clinvar_pathogenicity = re.compile(r'(' + '|'.join(map_clinvar_pathogenicity_keys) + r')', re.UNICODE|re.I)
    re_map_clinvar_review_status = re.compile(r'(' + '|'.join(map_clinvar_review_status_keys) + r')', re.UNICODE)

    getKnownGeneCanonical()
    getNullVariantLOF()
    getLOFGenes()
    getMissenseAAPathogenicity()
    getPubMedEval(df_pubmed)
    getDominantRecessiveDiseaseNames()
    getDiseasePrevalence()
    getORGreaterThan5Variants()
    getRecessiveDominantGenes()
    getRecessiveDominantVariants()
    getTopRankedGenes(df_hpo_ranking_genes)
    getBenignDomains()
    getRepeatRegion()
    getMissenseOrTruncatePathogenicityOfGene()
    getDisease2OMIMID()
    getOMIM2GeneReviewsName()
    getDiseasePenetrance()
    getGene2OMIM()

    variant_ACMG_score = dict()
    variant_ACMG_result = dict()
    variant_ACMG_weighted_score = dict()
    variant_ACMG_hit_criteria = dict()
    variant_ACMG_interpret = dict()
    variant_ACMG_interpret_chinese = dict()
    
    # Get pubmed articles that mention studied gene_variants
    pubmed_articles = dict()
    if not df_pubmed.empty:
        for index, row in df_pubmed.iterrows():
            gene, variant, title, journal, year, impact_factor, pmid = row['Gene'], row['Variant'], row['Title'], row['Journal'], row['Year'], row['Impact_Factor'], row['PMID']
            if (gene, variant) in pubmed_articles:
                pubmed_articles[(gene, variant)].append((pmid, title, journal, year, impact_factor))
            else:
                pubmed_articles[(gene, variant)] = [(pmid, title, journal, year, impact_factor)]

    # Get pubmed articles that mention studied genes
    pubmed_articles_genes_novariant = dict()
    if not df_pubmed_genes_novariant.empty:
        for index, row in df_pubmed_genes_novariant.iterrows():
            gene, title, journal, year, impact_factor, pmid = row['Gene'], row['Title'], row['Journal'], row['Year'], row['Impact_Factor'], row['PMID']
            if gene in pubmed_articles_genes_novariant:
                pubmed_articles_genes_novariant[gene].append((pmid, title, journal, year, impact_factor))
            else:
                pubmed_articles_genes_novariant[gene] = [(pmid, title, journal, year, impact_factor)]

    # Get pmids from variants clinvar records
    pmids_from_clinvar = []
    for key in variants.keys():
        variant_ = variants[key]
        clinvar_pmids_0 = variant_['clinvar_pmids']
        pmids_from_clinvar += clinvar_pmids_0
    pubmed_articles_from_clinvar = queryPubmedDB(pmids_from_clinvar)

    for key in variants.keys():
        variant_ = variants[key]
        #print variant_
        gene_0, variant_0, protein_0, id_0, rsid_0, transcript_0, effect_0, exon_0, interpro_domain_0, ref_0, alt_0, maf_exac_0, maf_1000g_0, maf_esp6500_0, dann_0, fathmm_0, metasvm_0, gerp_0, dbscSNV_rf_0, dbscSNV_ada_0, clinvar_pathogenicity_0, clinvar_pmids_0, clinvar_variation_ids_0, clinvar_review_status_0, zygosity_0, clinvar_diseases_0 = variant_['gene'], variant_['variant'], variant_['protein'], variant_['id'], variant_['rsid'], variant_['transcript'], variant_['effect'], variant_['exon'], variant_['interpro_domain'], variant_['ref'], variant_['alt'], variant_['maf_exac'], variant_['maf_1000g'], variant_['maf_esp6500'], variant_['dann'], variant_['fathmm'], variant_['metasvm'], variant_['gerp++'], variant_['dbscSNV_rf_score'], variant_['dbscSNV_ada_score'], variant_['clinvar_pathogenicity'], variant_['clinvar_pmids'], variant_['clinvar_variation_ids'], variant_['clinvar_review_status'], variant_['zygosity'], variant_['clinvar_associated_diseases']  
        
        clinvar_pmids_0_ = ["<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'> %s </a>" %(i,i) for i in clinvar_pmids_0]
        clinvar_variation_ids_0 = ["<a href='https://www.ncbi.nlm.nih.gov/clinvar/variation/%s/'> %s </a>" %(i,i) for i in clinvar_variation_ids_0.split('|')]

    	interpret, curr_interpret, interpret_chinese, curr_interpret_chinese = [], [], [], []   
    	if effect_0: 
                curr_interpret.append('Effect: %s.' % effect_0)
                curr_interpret_chinese.append('突变类型: %s.' % effect_0)
    	if interpro_domain_0: 
                curr_interpret.append('Protein domain: %s.' % '|'.join(interpro_domain_0))
                curr_interpret_chinese.append('蛋白功能区: %s.' % '|'.join(interpro_domain_0))
    	if id_0: 
                curr_interpret.append('HGVS ID: %s.' % id_0) 
                curr_interpret_chinese.append('HGVS ID: %s.' % id_0) 
    	if rsid_0: 
                curr_interpret.append("RefSeq ID: <a href='https://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=%s'> %s </a>"  % (rsid_0, rsid_0)) 
                curr_interpret_chinese.append("RefSeq ID: <a href='https://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=%s'> %s </a>"  % (rsid_0, rsid_0)) 
        if protein_0: 
                curr_interpret.append('Protein: %s.' % protein_0) 
                curr_interpret_chinese.append('蛋白质: %s.' % protein_0) 
    	if exon_0: 
                curr_interpret.append('exon: %s.' % exon_0) 
                curr_interpret_chinese.append('外显子: %s.' % exon_0) 
        if gene_0:
                # Add genecards link
                curr_interpret.append("GeneCards: <a href='http://www.genecards.org/cgi-bin/carddisp.pl?gene=%s'> %s </a>"  % (gene_0, gene_0))
                curr_interpret_chinese.append("GeneCards: <a href='http://www.genecards.org/cgi-bin/carddisp.pl?gene=%s'> %s </a>"  % (gene_0, gene_0))
                # Add OMIM link
                if gene_0 in gene2omim: 
                    omim_id = gene2omim[gene_0]
                    curr_interpret.append("OMIM: <a href='https://www.omim.org/entry/%s'> %s </a>"  % (omim_id, omim_id))
                    curr_interpret_chinese.append("OMIM: <a href='https://www.omim.org/entry/%s'> %s </a>"  % (omim_id, omim_id))
                # Add Decipher link
                curr_interpret.append("Decipher: <a href='https://decipher.sanger.ac.uk/search?q=%s#consented-patients/results'> %s </a>"  % (gene_0, gene_0))
                curr_interpret_chinese.append("Decipher: <a href='https://decipher.sanger.ac.uk/search?q=%s#consented-patients/results'> %s </a>"  % (gene_0, gene_0))
                # Add Genetics Home Reference link
                curr_interpret.append("Genetics Home Reference: <a href='https://ghr.nlm.nih.gov/gene/%s'> %s </a>"  % (gene_0, gene_0))
                curr_interpret_chinese.append("Genetics Home Reference: <a href='https://ghr.nlm.nih.gov/gene/%s'> %s </a>"  % (gene_0, gene_0))
                # Add GeneReviews link
                curr_interpret.append("GeneReviews: <a href='https://www.ncbi.nlm.nih.gov/books/NBK1116/?term=%s'> %s </a>"  % (gene_0, gene_0))
                curr_interpret_chinese.append("GeneReviews: <a href='https://www.ncbi.nlm.nih.gov/books/NBK1116/?term=%s'> %s </a>"  % (gene_0, gene_0))

    	if maf_exac_0:
                if id_0:
                    hgvs_id = id_0.replace('chr', '') 
                    hgvs_id = hgvs_id.replace(':', '-') 
                    hgvs_id = hgvs_id.replace('g.', '') 
                    hgvs_id = hgvs_id.replace('>', '') 
                    hgvs_id = hgvs_id.replace('A', '-A') 
                    hgvs_id = hgvs_id.replace('T', '-T') 
                    hgvs_id = hgvs_id.replace('C', '-C') 
                    hgvs_id = hgvs_id.replace('G', '-G') 
                    #print id_0, hgvs_id
                    curr_interpret.append("ExAC MAF: %s (<a href='http://exac.broadinstitute.org/variant/%s'> %s </a>)"  % (maf_exac_0, hgvs_id, hgvs_id)) 
                    curr_interpret_chinese.append("ExAC 最小等位基因频率(MAF): %s (<a href='http://exac.broadinstitute.org/variant/%s'> %s </a>)"  % (maf_exac_0, hgvs_id, hgvs_id)) 
                else:
                    curr_interpret.append('ExAC MAF: %s.' % maf_exac_0) 
                    curr_interpret_chinese.append('ExAC 最小等位基因频率(MAF): %s.' % maf_exac_0) 
                exac_details = variant_['exac_details']
                curr_interpret.append('ExAC MAF: Total Allele Count (%s), Total Allele Number (%s), Allele Frequency for all races (%s), Number of Homozygotes (%s), Homozygotes Percentage (%s), African Allele Count (%s), African Allele Number (%s), African Allele Frequency (%s), Latino Allele Count (%s), Latino  Allele Number (%s), Latino Allele Frequency (%s), East Asian Allele Count (%s), East Asian Allele Number (%s), East Asian Allele Frequency (%s), European (Finnish) Allele Count (%s), European (Finnish) Allele Number (%s), European (Finnish) Allele Frequency (%s), European (Non-Finnish) Allele Count (%s), European (Non-Finnish) Allele Number (%s), European (Non-Finnish) Allele Frequency (%s), Other Allele Count (%s), Other Allele Number (%s), Other Allele Frequency (%s), South Asian Allele Count (%s), South Asian Allele Number (%s), South Asian Allele Frequency (%s)' % (exac_details[0], exac_details[1], exac_details[2], exac_details[24], exac_details[25], exac_details[3], exac_details[4], exac_details[5], exac_details[6], exac_details[7], exac_details[8], exac_details[9], exac_details[10], exac_details[11], exac_details[12], exac_details[13], exac_details[14], exac_details[15], exac_details[16], exac_details[17], exac_details[18], exac_details[19], exac_details[20], exac_details[21], exac_details[22], exac_details[23]))

                curr_interpret_chinese.append('ExAC 最小等位基因频率(MAF)详细数据: Total Allele Count (%s), Total Allele Number (%s), Allele Frequency for all races (%s), Number of Homozygotes (%s), Homozygotes Percentage (%s), African Allele Count (%s), African Allele Number (%s), African Allele Frequency (%s), Latino Allele Count (%s), Latino  Allele Number (%s), Latino Allele Frequency (%s), East Asian Allele Count (%s), East Asian Allele Number (%s), East Asian Allele Frequency (%s), European (Finnish) Allele Count (%s), European (Finnish) Allele Number (%s), European (Finnish) Allele Frequency (%s), European (Non-Finnish) Allele Count (%s), European (Non-Finnish) Allele Number (%s), European (Non-Finnish) Allele Frequency (%s), Other Allele Count (%s), Other Allele Number (%s), Other Allele Frequency (%s), South Asian Allele Count (%s), South Asian Allele Number (%s), South Asian Allele Frequency (%s)' % (exac_details[0], exac_details[1], exac_details[2], exac_details[24], exac_details[25], exac_details[3], exac_details[4], exac_details[5], exac_details[6], exac_details[7], exac_details[8], exac_details[9], exac_details[10], exac_details[11], exac_details[12], exac_details[13], exac_details[14], exac_details[15], exac_details[16], exac_details[17], exac_details[18], exac_details[19], exac_details[20], exac_details[21], exac_details[22], exac_details[23]))

    	if maf_1000g_0: 
                curr_interpret.append('1000Genomes MAF: %s.' % maf_1000g_0) 
                curr_interpret_chinese.append('1000Genomes 最小等位基因频率(MAF): %s.' % maf_1000g_0) 
    	if maf_esp6500_0: 
                curr_interpret.append('Exome Sequencing Project(ESP) 6500 MAF: %s.' % maf_esp6500_0) 
                curr_interpret_chinese.append('Exome Sequencing Project(ESP) 6500 最小等位基因频率(MAF): %s.' % maf_esp6500_0) 
    	if dann_0: 
                curr_interpret.append('DANN pathogenicity score: %s (Pathogenicity Cutoff: 0.96).' % dann_0)
                curr_interpret_chinese.append('DANN致病性分数: %s (致病分数阈值: %s).' % (dann_0, '0.96'))
    	if fathmm_0: 
                curr_interpret.append('FATHMM pathogenicity score: %s (Pathogenicity Cutoff: 0.81415).' % fathmm_0)
                curr_interpret_chinese.append('FATHMM致病性分数: %s (致病分数阈值: %s).' % (fathmm_0, '0.81415'))
    	if metasvm_0: 
                curr_interpret.append('MetaSVM pathogenicity score: %s (Pathogenicity Cutoff: 0.83357).' % metasvm_0)
                curr_interpret_chinese.append('MetaSVM致病性分数: %s (致病分数阈值: %s).' % (metasvm_0, '0.83357'))
    	if gerp_0: 
                curr_interpret.append('GERP++ conservation score: %s (Pathogenicity Cutoff: 2.0).' % gerp_0)
                curr_interpret_chinese.append('GERP++序列保守性预测分数: %s (致病分数阈值: %s).' % (gerp_0, '2.0'))
    	if dbscSNV_rf_0: 
                curr_interpret.append('Random Forest dbscSNV splicing effect prediction: %s (Pathogenicity Cutoff: 0.6).' % dbscSNV_rf_0)
                curr_interpret_chinese.append('基于随机森林算法的dbscSNV剪接效应(splicing effect)预测分数: %s (致病分数阈值: %s).' % (dbscSNV_rf_0, '0.6'))
    	if dbscSNV_ada_0: 
                curr_interpret.append('AdaBoost dbscSNV splicing effect prediction: %s (Pathogenicity Cutoff: 0.6).' % dbscSNV_ada_0)
                curr_interpret_chinese.append('基于AdaBoost算法的dbscSNV剪接效应(splicing effect)预测分数: %s (致病分数阈值: %s).' % (dbscSNV_ada_0, '0.6'))
    	if clinvar_variation_ids_0 != ["<a href='https://www.ncbi.nlm.nih.gov/clinvar/variation//'>  </a>"]: 
                curr_interpret.append('Clinvar variation ids: %s.' % ",".join(clinvar_variation_ids_0))
                curr_interpret_chinese.append('Clinvar数据库ID: %s.' % ",".join(clinvar_variation_ids_0))
    	if clinvar_pathogenicity_0:
                joined_clinvar_pathogenicity_0 = []
                joined_clinvar_pathogenicity_chinese_0 = []
                for record in clinvar_pathogenicity_0:
                    description, submitter, datelastevaluated, method, comment = record
                    if not re.search('literature', method, re.I):
                        joined_clinvar_pathogenicity_0.append('Submitter-%s Submission time-%s Classification-%s' % (submitter, datelastevaluated, description)) 
                        joined_clinvar_pathogenicity_chinese_0.append('提交者-%s 提交时间-%s 致病性分类-%s' % (submitter, datelastevaluated, description)) 
                joined_clinvar_pathogenicity_0 = '; '.join(joined_clinvar_pathogenicity_0)
                joined_clinvar_pathogenicity_chinese_0 = '; '.join(joined_clinvar_pathogenicity_chinese_0)
                curr_interpret.append('Pathogenicity reported by Clinvar (Only showing clinical testing records): %s.' % joined_clinvar_pathogenicity_0)
                joined_clinvar_pathogenicity_0_chinese = re_map_clinvar_pathogenicity.sub(lambda m: map_clinvar_pathogenicity[m.group()], joined_clinvar_pathogenicity_chinese_0)
                curr_interpret_chinese.append('Clinvar数据库记录的变异致病性 (只显示临床试验(clinical testing)记录): %s.' % joined_clinvar_pathogenicity_0_chinese)
    	#if clinvar_review_status_0: 
        #        curr_interpret.append('Clinvar review status: %s.' % clinvar_review_status_0)
        #        clinvar_review_status_0_chinese = re_map_clinvar_review_status.sub(lambda m: map_clinvar_review_status[m.group()], clinvar_review_status_0)
        #        curr_interpret_chinese.append('Clinvar数据库记录审核状态: %s.' % clinvar_review_status_0)
    	if clinvar_pmids_0 and not pubmed_articles:
                clinvar_pubmed_articles = []
                for pmid in clinvar_pmids_0:
                    if pmid not in pubmed_articles_from_clinvar:
                        continue
                    title, journal, year, impact_factor, pathogenicity_score = pubmed_articles_from_clinvar[pmid]
                    clinvar_pubmed_articles.append("<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'> %s </a>: title: %s, journal: %s, year: %s, impact_factor: %s" %(pmid, pmid, title, journal, year, impact_factor))
                curr_interpret.append('Pubmed references from Clinvar: %s.' % "; ".join(clinvar_pubmed_articles))
                curr_interpret_chinese.append('Clinvar数据库记录的Pubmed相关生物医学文献: %s.' % "; ".join(clinvar_pubmed_articles))
        if clinvar_diseases_0:
                curr_interpret.append('Associated diseases from Clinvar: %s.' % clinvar_diseases_0)
                curr_interpret_chinese.append('Clinvar数据库记录的与此变异相关的疾病: %s.' % clinvar_diseases_0)
        if (gene_0, variant_0) in pubmed_articles.keys():
                pubmed_articles_0 = ["<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'> %s </a>: title: %s, journal: %s, year: %s, impact_factor: %s" %(i[0],i[0], i[1], i[2], i[3], i[4]) for i in pubmed_articles[(gene_0, variant_0)]]
                curr_interpret.append('Pubmed references: %s.' % "; ".join(pubmed_articles_0))
                curr_interpret_chinese.append('Pubmed相关生物医学文献: %s.' % "; ".join(pubmed_articles_0))
        elif not clinvar_pmids_0 and gene_0 in pubmed_articles_genes_novariant:
                pubmed_articles_0 = ["<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'> %s </a>: title: %s, journal: %s, year: %s, impact_factor: %s" %(i[0],i[0], i[1], i[2], i[3], i[4]) for i in pubmed_articles_genes_novariant[gene_0]]
                curr_interpret.append('Pubmed references: %s.' % "; ".join(pubmed_articles_0))
                curr_interpret_chinese.append('Pubmed相关生物医学文献: %s.' % "; ".join(pubmed_articles_0))

    	curr_interpret = '<br/>'.join(curr_interpret)
    	curr_interpret_chinese = '<br/>'.join(curr_interpret_chinese)
    	interpret.append(('variant_annotations', curr_interpret))
    	interpret_chinese.append(('变异注释', curr_interpret_chinese))

        # time.sleep(random.random())

    	PVS1 = check_PVS1(variant_)
    	PS1, PM5 = check_PS1_PM5(variant_)
    	PS2, PM6 = check_PS2_PM6(variant_, parent_ngs, parent_affects)
    	PS3, BS3 = check_PS3_BS3(variant_)
    	PS4 = check_PS4(variant_)
    	PM2 = check_PM2(variant_)
    	BA1, BS1 = check_BA1_BS1(variant_)
    	BS2 = check_BS2(variant_)
    	PM1 = check_PM1(variant_)
    	PM3, BP2 = check_PM3_BP2()
    	PM4, BP3 = check_PM4_BP3(variant_)
    	PP1, BS4 = check_PP1_BS4()
    	PP2, BP1 = check_PP2_BP1(variant_)
    	PP3, BP4 = check_PP3_BP4(variant_)
    	PP4 = check_PP4(variant_, gene_associated_phenos)
    	PP5, BP6 = check_PP5_BP6(variant_)
        # print 'PP5', PP5
        # print 'BP6', BP6
    	BP5 = check_BP5()
    	BP7 = check_BP7(variant_)
           
    	variant_ACMG_score[key] = ([PVS1, PS1, PS2, PS3, PS4, PM1, PM2, PM3, PM4, PM5, PM6, 
    				   PP1, PP2, PP3, PP4, PP5, BA1, BS1, BS2, BS3, BS4, 
    				   BP1, BP2, BP3, BP4, BP5, BP6, BP7])
    	classification_result, ACMG_weighted_score, hit_criteria = classify(variant_ACMG_score[key]) 
    	variant_ACMG_result[key] = classification_result
    	variant_ACMG_weighted_score[key] = ACMG_weighted_score 
    	variant_ACMG_hit_criteria[key] = hit_criteria
    	variant_ACMG_interpret[key] = interpret 
    	variant_ACMG_interpret_chinese[key] = interpret_chinese 

    variant_ACMG_score, variant_ACMG_result, variant_ACMG_weighted_score, variant_ACMG_hit_criteria, variant_ACMG_interpret, variant_ACMG_interpret_chinese = adjustPM3andBP2(variants, variant_ACMG_result, variant_ACMG_weighted_score, variant_ACMG_hit_criteria, variant_ACMG_score, variant_ACMG_interpret, variant_ACMG_interpret_chinese)

    final_result = []
    for key in variant_ACMG_weighted_score:
    	gene, variant = key
    	pathogenicity_score = variant_ACMG_weighted_score[key]
    	pathogenicity = variant_ACMG_result[key]
    	hit_criteria = variant_ACMG_hit_criteria[key]
    	variant_id = variants[key]['id']
        transcript = variants[key]['transcript']
    	final_result.append([gene, transcript, variant, variant_id, pathogenicity_score, pathogenicity, hit_criteria])

    df_final_result = pd.DataFrame(final_result, columns = ['gene', 'transcript', 'variant', 'id', 'pathogenicity_score', 'pathogenicity', 'hit_criteria'])
    if df_hpo_ranking_genes.shape[1] == 3:
        df_final_result = df_final_result.merge(df_hpo_ranking_genes, how = 'left', on = ['gene', 'variant'])
    elif df_hpo_ranking_genes.shape[1] == 2:
        df_final_result = df_final_result.merge(df_hpo_ranking_genes, how = 'left', on = 'gene')
    df_final_result.columns = ['gene', 'transcript', 'variant', 'id', 'pathogenicity_score', 'pathogenicity', 'hit_criteria', 'hpo_hit_score']
    df_final_result['final_score'] = df_final_result['hpo_hit_score'] * df_final_result['pathogenicity_score']
    df_final_result = df_final_result[['gene', 'transcript', 'variant', 'protein', 'id', 'final_score', 'pathogenicity_score', 'pathogenicity', 'hit_criteria', 'hpo_hit_score']]
    df_final_result.sort_values(by=['final_score'], ascending = [0], inplace = True)
    df_final_result['final_score'] = df_final_result['final_score'].apply(lambda x: round(x,2))
    df_final_result.drop_duplicates(subset = ['gene', 'variant'], inplace = True)
    df_final_result = df_final_result.reset_index(drop=True)

    gene_list = list(df_final_result['gene'])
    variant_list = list(df_final_result['variant'])
    gene_variant_list = [(gene_list[i], variant_list[i]) for i in range(len(gene_list))]

    df_variant_ACMG_interpret = pd.DataFrame()
    df_variant_ACMG_interpret_chinese = pd.DataFrame() 
    for key in gene_variant_list:
        tmp_df = pd.DataFrame(variant_ACMG_interpret[key], columns = ['criteria', 'interpretation'])
        tmp_df['gene'] = key[0]
        tmp_df['variant'] = key[1]
        tmp_df = tmp_df[['gene', 'variant', 'criteria', 'interpretation']] 
        df_variant_ACMG_interpret = pd.concat([df_variant_ACMG_interpret, tmp_df])

        tmp_df = pd.DataFrame(variant_ACMG_interpret_chinese[key], columns = ['criteria', 'interpretation'])
        tmp_df['gene'] = key[0]
        tmp_df['variant'] = key[1]
        tmp_df = tmp_df[['gene', 'variant', 'criteria', 'interpretation']] 
        df_variant_ACMG_interpret_chinese = pd.concat([df_variant_ACMG_interpret_chinese, tmp_df])

    return df_final_result, variant_ACMG_interpret, variant_ACMG_interpret_chinese, df_variant_ACMG_interpret, df_variant_ACMG_interpret_chinese
