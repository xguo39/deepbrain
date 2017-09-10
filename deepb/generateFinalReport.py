# -*- coding: utf-8 -*-

import json
import pandas as pd
import os
import sys
import re

BASE = os.path.dirname(os.path.abspath(__file__))

reload(sys)
sys.setdefaultencoding('utf-8')

def readCHPOFile():
    df = pd.read_csv(os.path.join(BASE, 'data/chpo_2016_10.txt'), sep = '\t')    
    hpoid_to_category, hpoid_to_english_name, hpoid_to_chinese_name, hpoid_to_english_definition, hpoid_to_chinese_definition = dict(), dict(), dict(), dict(), dict()
    hpoid_to_category = df.set_index('HPO编号').to_dict()['主分类(中文)']
    hpoid_to_english_name = df.set_index('HPO编号').to_dict()['名称(英文)']
    hpoid_to_chinese_name = df.set_index('HPO编号').to_dict()['名称(中文)']
    hpoid_to_english_definition = df.set_index('HPO编号').to_dict()['定义(英文)']
    hpoid_to_chinese_definition = df.set_index('HPO编号').to_dict()['定义(中文)']
    return hpoid_to_category, hpoid_to_english_name, hpoid_to_chinese_name, hpoid_to_english_definition, hpoid_to_chinese_definition

def generatePrimaryFindings(df_final_res, variant_ACMG_interpret_chinese, variants, pheno_to_hpo_pheno_and_id=None):
    ### Primary findings
    primary_findings_info = 'These genetic findings have been identified as the most relevant to the reported phenotype(s). These variants are deemed to be potentially pathogenic as determined by a combination of curated databases of disease association, and predicted severity of the mutations. Substitutions and other small (<50 bp) genetic variants:'

    variant_information = []
    variant_information.append(('Variant name', 'Coding effect', 'Zygosity', 'Associated phenotypes', 'Population freq'))    
    interpretation_details = [] 
    num_variants_to_report = 3 
    i = 0
    for index, row in df_final_res.iterrows():
        if pheno_to_hpo_pheno_and_id: 
            gene, transcript, variant, protein, id, zygosity, correlated_phenotypes = row['gene'], row['transcript'], row['variant'], row['protein'], row['id'], row['zygosity'], row['correlated_phenotypes']
        else: 
            gene, transcript, variant, protein, id, zygosity = row['gene'], row['transcript'], row['variant'], row['protein'], row['id'], row['zygosity']
            correlated_phenotypes = ''
        variant_name = '; '.join([gene, transcript, variant, protein, id])
        pop_freq = variants[(gene, variant)]['maf_exac']
        coding_effect = variants[(gene, variant)]['effect']
        df_interpretation = variant_ACMG_interpret_chinese[(variant_ACMG_interpret_chinese.gene == gene) & (variant_ACMG_interpret_chinese.variant == variant)]
        interpretation_list = []

        maf_exac, maf_1000g, maf_esp6500 = variants[(gene, variant)]['maf_exac'], variants[(gene, variant)]['maf_1000g'], variants[(gene, variant)]['maf_esp6500']
        dann, fathmm, metasvm, gerp, dbscSNV_rf, dbscSNV_ada = variants[(gene, variant)]['dann'], variants[(gene, variant)]['fathmm'], variants[(gene, variant)]['metasvm'], variants[(gene, variant)]['gerp++'], variants[(gene, variant)]['dbscSNV_rf_score'], variants[(gene, variant)]['dbscSNV_ada_score']
        if maf_exac: interpretation_list.append('ExAC最小等位基因频率(MAF)是%s' % maf_exac)
        if maf_1000g: interpretation_list.append('1000Genomes最小等位基因频率(MAF)是%s' % maf_1000g)
        if maf_esp6500: interpretation_list.append('Exome Sequencing Project(ESP) 6500最小等位基因频率(MAF)是%s' % maf_esp6500)
        if dann: interpretation_list.append('DANN致病性分数: %s (致病分数阈值: %s)' % (dann, '0.96')) 
        if fathmm: interpretation_list.append('FATHMM致病性分数: %s (致病分数阈值: %s)' % (fathmm, '0.81415')) 
        if metasvm: interpretation_list.append('MetaSVM致病性分数: %s (致病分数阈值: %s)' % (metasvm, '0.83357')) 
        if gerp: interpretation_list.append('GERP++致病性分数: %s (致病分数阈值: %s)' % (gerp, '2.0')) 
        if dbscSNV_rf: interpretation_list.append('基于随机森林算法的dbscSNV剪接效应 (splicing effect) 预测分数: %s (致病分数阈值: %s)' % (dbscSNV_rf, '0.6')) 
        if dbscSNV_ada: interpretation_list.append('基于AdaBoost算法的dbscSNV剪接效应 (splicing effect) 预测分数: %s (致病分数阈值: %s)' % (dbscSNV_ada, '0.6')) 
       
        for index_, row_ in df_interpretation.iterrows():
            criteria, interpretation = row_['criteria'], row_['interpretation']
            if criteria == '变异注释' or criteria == 'PP3和BP4':
                continue
            criterias = criteria.split('和')
            interpretations = interpretation.split('.')
            interpretations = [_ for _ in interpretations if _]
            if len(criterias) == 1 and not re.search(r'不符合', interpretation):
                interpretation_list += interpretations[0:-1]
            elif len(criterias) == 2 and len(re.findall(r'不符合', interpretation)) != 2:
                interpretation_list += interpretations[0:-2]
        variant_information.append((variant_name, coding_effect, zygosity, correlated_phenotypes, pop_freq))
        interpretation_detail = '. '.join(interpretation_list)
        interpretation_detail += '.'
        interpretation_details.append((gene+' '+protein, interpretation_detail))
        i += 1
        if i >= num_variants_to_report:
            break
    return variant_information, interpretation_details

def generateSecondaryFindings(variant_ACMG_interpret_chinese, variants, pheno_to_hpo_pheno_and_id=None, df_incidental_findings_genes=None):
    ### Secondary findings
    if not df_incidental_findings_genes: 
        return [], []

    secondary_findings_info = "These genetic findings have been identified as less certainly relevant to the reported phenotype(s). These variants are deemed to be potentially pathogenic as determined by a combination of curated databases of disease association, and predicted severity of the mutations. Substitutions and other small(<50 bp) genetic variants: "

    secondary_variant_information = []
    secondary_variant_information.append(('Variant name', 'Coding effect', 'Zygosity', 'Associated phenotypes', 'Population freq'))    
    secondary_interpretation_details = [] 
    num_variants_to_report = 10
    i = 0
    for index, row in df_incidental_findings_genes.iterrows():
        gene, transcript, variant, protein, id, zygosity, hit_criteria, correlated_phenotypes = row['gene'], row['transcript'], row['variant'], row['protein'], row['id'], row['zygosity'], row['hit_criteria'], row['correlated_phenotypes']
        variant_name = '; '.join([gene, transcript, variant, protein, id])
        pop_freq = variants[(gene, variant)]['maf_exac']
        coding_effect = variants[(gene, variant)]['effect']
        df_interpretation = variant_ACMG_interpret_chinese[(variant_ACMG_interpret_chinese.gene == gene) & (variant_ACMG_interpret_chinese.variant == variant)]
        interpretation_list = []

        maf_exac, maf_1000g, maf_esp6500 = variants[(gene, variant)]['maf_exac'], variants[(gene, variant)]['maf_1000g'], variants[(gene, variant)]['maf_esp6500']
        dann, fathmm, metasvm, gerp, dbscSNV_rf, dbscSNV_ada = variants[(gene, variant)]['dann'], variants[(gene, variant)]['fathmm'], variants[(gene, variant)]['metasvm'], variants[(gene, variant)]['gerp++'], variants[(gene, variant)]['dbscSNV_rf_score'], variants[(gene, variant)]['dbscSNV_ada_score']
        if maf_exac: interpretation_list.append('ExAC最小等位基因频率(MAF)是%s' % maf_exac)
        if maf_1000g: interpretation_list.append('1000Genomes最小等位基因频率(MAF)是%s' % maf_1000g)
        if maf_esp6500: interpretation_list.append('Exome Sequencing Project(ESP) 6500最小等位基因频率(MAF)是%s' % maf_esp6500)
        if dann: interpretation_list.append('DANN致病性分数: %s (致病分数阈值: %s)' % (dann, '0.96')) 
        if fathmm: interpretation_list.append('FATHMM致病性分数: %s (致病分数阈值: %s)' % (fathmm, '0.81415')) 
        if metasvm: interpretation_list.append('MetaSVM致病性分数: %s (致病分数阈值: %s)' % (metasvm, '0.83357')) 
        if gerp: interpretation_list.append('GERP++致病性分数: %s (致病分数阈值: %s)' % (gerp, '2.0')) 
        if dbscSNV_rf: interpretation_list.append('基于随机森林算法的dbscSNV剪接效应 (splicing effect) 预测分数: %s (致病分数阈值: %s)' % (dbscSNV_rf, '0.6')) 
        if dbscSNV_ada: interpretation_list.append('基于AdaBoost算法的dbscSNV剪接效应 (splicing effect) 预测分数: %s (致病分数阈值: %s)' % (dbscSNV_ada, '0.6')) 
       
        for index_, row_ in df_interpretation.iterrows():
            criteria, interpretation = row_['criteria'], row_['interpretation']
            if criteria == '变异注释' or criteria == 'PP3和BP4':
                continue
            criterias = criteria.split('和')
            interpretations = interpretation.split('.')
            interpretations = [_ for _ in interpretations if _]
            if len(criterias) == 1 and not re.search(r'不符合', interpretation):
                interpretation_list += interpretations[0:-1]
            elif len(criterias) == 2 and len(re.findall(r'不符合', interpretation)) != 2:
                interpretation_list += interpretations[0:-2]
        secondary_variant_information.append((variant_name, coding_effect, zygosity, correlated_phenotypes, pop_freq))
        interpretation_detail = '. '.join(interpretation_list)
        interpretation_detail += '.'
        secondary_interpretation_details.append((gene+' '+protein, interpretation_detail))
        i += 1
        if i >= num_variants_to_report:
            break
    return secondary_variant_information, secondary_interpretation_details


def generateFinalReport(df_final_res, variant_ACMG_interpret_chinese, variants, pheno_to_hpo_pheno_and_id=None, df_incidental_findings_genes=None):
    ''' df_final_res is a pandas dataframe sorted by final_score, ['gene', 'transcript', 'variant', 'protein', 'id', 'zygosity','correlated_phenotypes', 'pheno_match_score', 'hit_criteria', 'pathogenicity', 'pathogenicity_score', 'final_score']
        variant_ACMG_interpret_chinese is a pandas dataframe, ['gene', 'variant', 'criteria', 'interpretation'] 
        variants is a dict of dict [key][property]
    '''
    ###### Order information ######
    order_information = {} 
    patient_information = []
    test_code = '14852975430'
    ordering_physician = 'Alex Xu'
    patient_name = 'James Huang'
    hospital = 'CHOP'
    patient_dob = '2014-03-09'
    patient_gender = 'Male'
    date_of_report = '2017-09-12'
    proband_code, father_code, mother_code = 'Patient1', 'Patient1F', 'Patient1M'
    proband_affected, father_affected, mother_affected = 'YES', 'NO', 'NO' 
    proband_specimen_type, father_specimen_type,  mother_specimen_type = 'Blood', 'Blood', 'Blood' 
    father_dob, mother_dob = '1984-05-28', '1986-01-04' 
    proband_date_collected, father_date_collected, mother_date_collected = '2017-09-01', '2017-09-01', '2017-09-01' 
    proband_date_received, father_date_received, mother_date_received = '2017-09-02', '2017-09-02', '2017-09-02' 

    order_information = {'test_code':test_code, 'ordering_physician':ordering_physician, 'patient_name':patient_name, 'hospital':hospital, 'patient_dob':patient_dob, 'patient_gender':patient_gender, 'date_of_report':date_of_report}   
 
    patient_information = [
        ('', 'Patient Code', 'Gender', 'Date of Birth', 'Affected', 'Specimen type', 'Date collected', 'Date received'),
        ('Proband', proband_code, patient_gender, patient_dob, proband_affected, proband_specimen_type, proband_date_collected, proband_date_received),
        ('Father', father_code, 'Male', father_dob, father_affected, father_specimen_type, father_date_collected, father_date_received),
        ('Mother', mother_code, 'Female', mother_dob, mother_affected, mother_specimen_type, mother_date_collected, mother_date_received)]

    #print order_information
    #print patient_information

    ### Patient information
    hpoid_to_category, hpoid_to_english_name, hpoid_to_chinese_name, hpoid_to_english_definition, hpoid_to_chinese_definition = readCHPOFile() 
    phenotype_information = []
    phenotype_information.append(('Name (English)', 'Name (Chinese)', 'HPO ID', 'Category', 'Definition (English)', 'Definition (Chinese)'))
    if pheno_to_hpo_pheno_and_id:
        for pheno in pheno_to_hpo_pheno_and_id:
            max_sim_hpo_pheno, max_sim_hpoid = pheno_to_hpo_pheno_and_id[pheno]
            try:
                category, english_name, chinese_name, english_definition, chinese_definition = hpoid_to_category[max_sim_hpoid], hpoid_to_english_name[max_sim_hpoid], hpoid_to_chinese_name[max_sim_hpoid], hpoid_to_english_definition[max_sim_hpoid], hpoid_to_chinese_definition[max_sim_hpoid] 
                phenotype_information.append((english_name, chinese_name, max_sim_hpoid, category, english_definition, chinese_definition)) 
            except KeyError:
                pass
    #print phenotype_information
 
    ### General information
    general_information = 'This genetic test report is based on analysis of raw data of Whole Exome Sequencing. The report is intended for clinical diagnostic use. The sequencing protocol performed on the samples is of clinical grade, and is certified for diagnostic use. The primary purpose of this report is to communicate variants with strong evidence supporting their association to the reported phenotype(s). Incidental germline findings that do not correlate with the provided phenotype(s) are included in this report in the Incidental Findings section, if elected to be included in the report by the patient or legal guardian. Not all detected variants have been analyzed, and not all regions of the genome have been adequately sequenced. These results should be interpreted in the context of the patient’s medical evaluation, family history, and genealogy. Please note that variant classification and/or interpretation may change over time as more information becomes available.'

    ###### Results of Genetic Testing ###### 
    parimary_variant_information, primary_interpretation_details = generatePrimaryFindings(df_final_res, variant_ACMG_interpret_chinese, variants, pheno_to_hpo_pheno_and_id=None)
    secondary_variant_information, secondary_interpretation_details = generateSecondaryFindings(variant_ACMG_interpret_chinese, variants, pheno_to_hpo_pheno_and_id=None, df_incidental_findings_genes=None)
    #print parimary_variant_information
    #print primary_interpretation_details
    #print secondary_variant_information
    #print secondary_interpretation_details

    ###### Test Information and Limitations ######
    limitations = "Whole Exome Sequencing (WES) is one of the most comprehensive tools for detection of rare disease causing and associated variants in human DNA. Whole Exome includes all the expressed and majority of the transcribed regions in human genome, and it is estimated to cover over 85% of known and to be discovered disease causing genetic variants. While all types of mutations are detectable, some genetic aberrations, such as gross structural variants, genomic rearrangements or variants in portions of genes with highly homologous pseudogenes, are called with significantly lower efficiency. Thus, the test is not intended to detect gross deletions or duplications, gross rearrangements, intronic or intergenic variants. The test is also not intended to detect aberrations not caused by variants in DNA sequence, such as gene expression, epigenetic modifications, fusion, chromosome conformational changes, X-linked recessive mutations in females who manifest disease due to skewed X-inactivation and other unknown abnormalities. A negative result from the analysis cannot rule out the possibility that the tested individual carries a rare unexamined mutation or mutation in an undetectable region (see statistics table below). Next generation sequencing technologies, including WES analysis, may generate false positive calls. Any clinically relevant variant identified by NGS is recommended by current best practice guidelines to be validated by orthogonal technology such as Sanger sequencing to confirm if it is a true positive. The test has not been cleared or approved by the US Food and Drug Administration. The FDA does not require this test to go through premarket FDA review."

    return order_information, patient_information, phenotype_information, general_information, parimary_variant_information, primary_interpretation_details, secondary_variant_information, secondary_interpretation_details, limitations
