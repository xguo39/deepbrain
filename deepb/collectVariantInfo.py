import myvariant
import re
import pandas as pd
import time
import sys
import mygene
import argparse
import amino_acid_mapping
import Levenshtein
import random
from collections import defaultdict
# import pickle
# import pprint

reload(sys)
sys.setdefaultencoding('utf-8')
pd.options.display.max_colwidth = 10000

CLINVAR_VARIANT_SUMMARY = 'data/clinvar_variant_summary.txt'
PARSED_CLINVAR = 'data/parsed_clinvar.txt'
# SAMPLE_GENES = 'data/sample_genes.txt'


## Collect information from myvariant 

def collectAll(gene, variant, transcript):
  mv = myvariant.MyVariantInfo()
  snpeff = mv.query('snpeff.ann.gene_id:%s AND snpeff.ann.hgvs_c:%s'
		     % (gene, variant), fields='snpeff')
  try:
    variant_id = snpeff['hits'][0]['_id']
  except IndexError:
    return '', '', '', '', '', '', '' 
  hits = snpeff['hits']
  anns = []
  variant_ids = []
  scores = []
  # There can be multiple hits; scan all hits to find out the variant_id that match gene, variant, and transcript
  for hit in hits:
    variant_ids.append(hit['_id'])
    scores.append(hit['_score'])
    ann = hit['snpeff']['ann']
    anns.append(ann)

  max_similarity = 0
  max_score = 0

  for ind in xrange(len(anns)):
    ann = anns[ind]
    tmp_variant_id = variant_ids[ind]
    score = scores[ind]
    if isinstance(ann, dict):
      ann = [ann]
    transcript = transcript.decode('utf-8')
    for var in ann:
      if var['hgvs_c'] == variant and var['gene_id'] == gene:    
        sim = Levenshtein.ratio(transcript, var['feature_id'])
        if sim >= max_similarity:
          if sim == max_similarity and score < max_score:
            continue
          max_similarity = sim
          max_score = score
          effect, feature_id, feature_type, putative_impact, transcript_biotype = (var['effect'], var['feature_id'], var['feature_type'], var['putative_impact'], var['transcript_biotype'])
          hgvs_p = var['hgvs_p'] if 'hgvs_p' in var else ''
          variant_id = tmp_variant_id

  return variant_id, effect, feature_id, feature_type, putative_impact, transcript_biotype, hgvs_p 

def collectExAC():
  try:
    maf_exac = float(non_snpeff['exac']['ac']['ac_adj']) / non_snpeff['exac']['an']['an_adj']
  except KeyError:
    maf_exac = '' 
  except TypeError:
    try:
      maf_exac = float(max(non_snpeff['exac']['ac']['ac_adj'])) / non_snpeff['exac']['an']['an_adj']
    except ZeroDivisionError:
      maf_exac = '' 
  except ZeroDivisionError:
    maf_exac = '' 
  try:
    maf_exac_nontcga = float(non_snpeff['exac_nontcga']['ac']['ac_adj']) / non_snpeff['exac_nontcga']['an']['an_adj']
  except KeyError:
    maf_exac_nontcga = '' 
  except TypeError:
    try:
      maf_exac_nontcga = float(max(non_snpeff['exac_nontcga']['ac']['ac_adj'])) / non_snpeff['exac_nontcga']['an']['an_adj']
    except ZeroDivisionError:
      maf_exac_nontcga = ''
  except ZeroDivisionError:
    maf_exac_nontcga = '' 
  return str(maf_exac), str(maf_exac_nontcga)

def collectdbNSFP():
  threshold = {'dann':0.96, 'fathmm':0.81415, 'metasvm':0.83357, 'gerp++':2.0}

  if 'dbnsfp' not in non_snpeff:
    dann = fathmm = metasvm = gerp = ''
    interpro_domain = [] 
  else:
    try:
      dann = non_snpeff['dbnsfp']['dann']['score']
    except KeyError:
      dann = '' 
    try:
      fathmm = non_snpeff['dbnsfp']['fathmm']['rankscore']
    except KeyError:
      fathmm = '' 
    try:
      metasvm = non_snpeff['dbnsfp']['metasvm']['rankscore']
    except KeyError:
      metasvm = '' 
    try:
      gerp = non_snpeff['dbnsfp']['gerp++']['rs']
    except KeyError:
      gerp = '' 
    try:
      interpro_domain = non_snpeff['dbnsfp']['interpro_domain']
      if not isinstance(interpro_domain, list): interpro_domain = [interpro_domain]
    except KeyError:
      interpro_domain = [] 
  pathogenicity_scores = [str(dann), str(fathmm), str(metasvm), str(gerp)]
  return pathogenicity_scores, interpro_domain # interpro_domain is a list

def collectMAF():
  try:
    cadd_1000g = non_snpeff['cadd']['1000g']['af']
  except KeyError:
    cadd_1000g = ''
  try:
    cadd_esp = non_snpeff['cadd']['esp']['af']
  except KeyError:
    cadd_esp = ''
  try:
    dbnsfp_1000g = non_snpeff['dbnsfp']['1000gp3']['af']
  except KeyError:
    dbnsfp_1000g = ''
  try:
    dbnsfp_exac = non_snpeff['dbnsfp']['exac']['adj_af']
  except KeyError:
    dbnsfp_exac = ''
  maf = [str(dbnsfp_exac), str(dbnsfp_1000g), str(cadd_1000g), str(cadd_esp)]
  return maf

def getClinvarField(keyword, db):
  if keyword == 'conditions':
    if isinstance(db[keyword], list):
      conditions = []
      for cond in db[keyword]:
        if 'name' in cond:
          conditions.append(cond['name'])
      return '|'.join(conditions)
    else:
      return db[keyword]['name'] 
  if keyword in db:
    return db[keyword]
  else:
    return ''

def collectClinvar():
  if 'clinvar' not in non_snpeff or 'rcv' not in non_snpeff['clinvar']:
    return '' 
  rcv = non_snpeff['clinvar']['rcv']
  clinvar_data = []
  if isinstance(rcv, dict):
    rcv = [rcv]
  for case in rcv: 
    pathogenicity = getClinvarField('clinical_significance', case)
    date_last_evaluated = getClinvarField('last_evaluated', case)
    clinvar_data.append(pathogenicity) 
  return '|'.join(clinvar_data)

def collectCadd():
  if 'cadd' not in non_snpeff:
    annotype = consequence = consdetail = grantham_score = phred_score = exon = ''
  else:
    annotype = non_snpeff['cadd']['annotype'] if 'annotype' in non_snpeff['cadd'] else ''
    if isinstance(annotype, list): annotype = '|'.join(annotype)
    consequence = non_snpeff['cadd']['consequence'] if 'consequence' in non_snpeff['cadd'] else ''
    if isinstance(consequence, list): consequence = '|'.join(consequence)
    consdetail = non_snpeff['cadd']['consdetail'] if 'consdetail' in non_snpeff['cadd'] else ''
    if isinstance(consdetail, list): consdetail = '|'.join(consdetail)
    grantham_score = non_snpeff['cadd']['grantham'] if 'grantham' in non_snpeff['cadd'] else ''
    phred_score = non_snpeff['cadd']['phred'] if 'phred' in non_snpeff['cadd'] else ''
    exon = non_snpeff['cadd']['exon'] if 'exon' in non_snpeff['cadd'] else ''
    if isinstance(exon, list): exon = exon[0]
  return annotype, consequence, consdetail, grantham_score, phred_score, exon

def collectVCF():
  if 'vcf' not in non_snpeff: return '', ''
  ref = non_snpeff['vcf']['ref'] if 'ref' in non_snpeff['vcf'] else ''
  alt = non_snpeff['vcf']['alt'] if 'alt' in non_snpeff['vcf'] else ''
  return ref, alt

def collectdbsnp():
  if 'dbsnp' not in non_snpeff: return ''
  rsid = non_snpeff['dbsnp']['rsid'] if 'rsid' in non_snpeff['dbsnp'] else ''
  return rsid

# Read clinvar summary data, from which we get clinvar title to gene mapping
def initClinvarTitle2GeneDict():
  global title2gene
  global CLINVAR_VARIANT_SUMMARY
  df_clinvar_summary = pd.read_csv(CLINVAR_VARIANT_SUMMARY, sep = '\t', usecols = ['Name', 'GeneSymbol'])
  title2gene = df_clinvar_summary.set_index('Name').to_dict()['GeneSymbol']

def getClinvarData():
  global PARSED_CLINVAR
  clinvar_pathogenicity = dict()
  pathos= []
  with open(PARSED_CLINVAR, 'rb') as f:
    f.readline()
    for line in f.readlines():
      line = line.rstrip()
      parts = line.split('\t')
      title, variant, pathogenicity = parts[1], parts[3], parts[8]
      pathos.append(pathogenicity)
      # Convert protein from 1 to 3 letters
      variants = variant.split('|')
      variants = [item.split(':')[-1] for item in variants if item]
      try:
        gene = title2gene[title.split(' AND ')[0]]
      except KeyError:
        try:
          gene = title.split(':')[0].split('(')[1].rstrip(')')
        except IndexError:
          gene = ''
      for variant in variants:
        if (gene, variant) not in clinvar_pathogenicity:
          clinvar_pathogenicity[(gene, variant)] = [pathogenicity]
        else:
          clinvar_pathogenicity[(gene, variant)].append(pathogenicity)
    for key in clinvar_pathogenicity:
      values = clinvar_pathogenicity[key]
      values = '|'.join(values)
      clinvar_pathogenicity[key] = values
    # print set(pathos)
  return clinvar_pathogenicity

# def readCandidateGenes(hpo_filtered_genes):
#   global SAMPLE_GENES
#   candidate_vars = []
#   # df_hpo_filtered_genes = pd.read_csv('result/ranking_genes.txt', sep = '\t')
#   # hpo_filtered_genes = pd.unique(df_hpo_filtered_genes['gene'].values).tolist()
#   with open(SAMPLE_GENES, 'rb') as f:
#     f.readline()
#     for line in f.readlines():
#       line = line.rstrip()
#       parts = line.split('\t')
#       gene = parts[0]
#       if gene not in hpo_filtered_genes:
#         continue
#       for part in parts:
#         if re.search(r'_.*:', part):
#           transcript, variant = part.split(':') 
#       candidate_vars.append((gene, variant, transcript))
#   return candidate_vars


def get_variants(candidate_vars):

  mv = myvariant.MyVariantInfo()
  variant_ids = []
  variant_id2key = dict()
  variants = defaultdict(dict)

  # The dbscsnv (splicing effect prediction) can not be obtained from myvariant; instead, we have local flat dbscsnv files
  dbscsnv_chromosomes, dbscsnv_variants = [], {}
  for var in candidate_vars:
    # print var
    gene, variant, transcript = var
    key = (gene, variant)
    variant_id, effect, feature_id, feature_type, putative_impact, transcript_biotype, hgvs_p = collectAll(gene, variant, transcript)
    variants[key]['gene'], variants[key]['variant'], variants[key]['transcript'] = gene, variant, transcript
    variants[key]['id'], variants[key]['effect'], variants[key]['protein'] = variant_id, effect, hgvs_p 
    
    # Only 'interpro_domain' is a list; all the other fields are strings 
    if not variant_id:
      variants[key]['maf_exac'] = variants[key]['maf_1000g'] = variants[key]['maf_esp6500'] = variants[key]['dann'] = variants[key]['fathmm'] = variants[key]['metasvm'] = variants[key]['gerp++'] = variants[key]['exon'] = variants[key]['ref'] = variants[key]['alt'] = variants[key]['rsid'] = ''
      variants[key]['interpro_domain'] = []
      variants[key]['clinvar_pathogenicity'] = '' 
      continue
    variant_ids.append(variant_id)
    variant_id2key[variant_id] = (gene, variant)
    # time.sleep(random.uniform(0.1, 0.3))

  non_snpeff_var_data = mv.getvariants(variant_ids, fields = ['exac.ac.ac_adj','exac.an.an_adj', 'exac_nontcga.ac.ac_adj', 'exac_nontcga.an.an_adj',
                               'dbnsfp', 'cadd.1000g.af', 'cadd.esp.af', 'clinvar.omim', 'clinvar.rcv',
                               'cadd.annotype', 'cadd.consequence', 'cadd.consdetail', 'cadd.grantham',
                               'cadd.phred', 'cadd.exon', 'vcf.ref', 'vcf.alt', 'dbsnp.rsid'])
  global non_snpeff
  for data in non_snpeff_var_data:
    non_snpeff = data
    variant_id = non_snpeff['_id'] 
    key = variant_id2key[variant_id]

    maf_exac, maf_exac_nontcga = collectExAC()
    maf_exac = maf_exac_nontcga if not maf_exac and maf_exac_nontcga else maf_exac

    dbnsfp_exac, dbnsfp_1000g, cadd_1000g, cadd_esp = collectMAF()
    variants[key]['maf_exac'] = dbnsfp_exac if dbnsfp_exac else maf_exac
    variants[key]['maf_1000g'] = dbnsfp_1000g if dbnsfp_1000g else cadd_1000g
    variants[key]['maf_esp6500'] = cadd_esp

    pathogenicity_scores, interpro_domain = collectdbNSFP()
    dann, fathmm, metasvm, gerp = pathogenicity_scores 
    variants[key]['dann'], variants[key]['fathmm'], variants[key]['metasvm'], variants[key]['gerp++'] = dann, fathmm, metasvm, gerp
    variants[key]['interpro_domain'] = interpro_domain

    clinvar_data = collectClinvar()
    variants[key]['clinvar_pathogenicity'] = clinvar_data

    annotype, consequence, consdetail, grantham_score, phred_score, exon = collectCadd()
    variants[key]['exon'] = exon.split('/')[0]

    ref, alt = collectVCF()
    variants[key]['ref'], variants[key]['alt'] = ref, alt
   
    rsid = collectdbsnp()
    variants[key]['rsid'] = rsid

    chromosome = variant_id.split(':')[0]
    allele_start_pos = re.findall(r'[0-9]{1,20}', variant_id.split('.')[-1])[0]
    dbscsnv_chromosomes.append(chromosome) 
    dbscsnv_variants[(chromosome, allele_start_pos, ref, alt)] = key

  ## Get dbscSNV splicing effect data from local files
  # print "Get dbscSNV splicing data "
  for chromosome in set(dbscsnv_chromosomes):
    # print chromosome
    with open('data/dbscSNV/dbscSNV1.1.' + chromosome, 'rb') as f:
      f.readline()
      for line in f.readlines():
        line = line.rstrip()
        parts = line.split('\t')
        chromo, pos, ref, alt, ada_score, rf_score = 'chr' + parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
        if (chromo, pos, ref, alt) in dbscsnv_variants:
          variants[dbscsnv_variants[(chromo, pos, ref, alt)]]['dbscSNV_rf_score'] = rf_score
          variants[dbscsnv_variants[(chromo, pos, ref, alt)]]['dbscSNV_ada_score'] = ada_score
  for key in variants.keys():
    if 'dbscSNV_rf_score' not in variants[key] or variants[key]['dbscSNV_rf_score'] == '.': variants[key]['dbscSNV_rf_score'] = ''
    if 'dbscSNV_ada_score' not in variants[key] or variants[key]['dbscSNV_ada_score'] == '.': variants[key]['dbscSNV_ada_score'] = ''

  ## Get Clinvar assertion data from local file if the record can not be find in myvariant
  # print "Get Clinvar data "
  initClinvarTitle2GeneDict()
  clinvar_pathogenicity = getClinvarData()
  for key in variants.keys():
    if not variants[key]['clinvar_pathogenicity'] and key in clinvar_pathogenicity:
      variants[key]['clinvar_pathogenicity'] = clinvar_pathogenicity[key]

  # pprint.pprint(variants)
  # pickle.dump(variants, open('result/variants.p', 'wb'))

  final_res = []
  for key in variants:
    v = variants[key]
    # final_res.append([v['gene'], v['variant'], v['protein'], v['id'], v['rsid'], v['transcript'], v['effect'], v['exon'], v['interpro_domain'], v['ref'], v['alt'], v['maf_exac'], v['maf_1000g'], v['maf_esp6500'], v['dann'], v['fathmm'], v['metasvm'], v['gerp++'], v['dbscSNV_rf_score'], v['dbscSNV_ada_score'], v['clinvar_pathogenicity']])
    final_res.append((v['gene'], v['variant'], v['protein']))
  # df_final_res = pd.DataFrame(final_res, columns = ['gene', 'variant', 'protein', 'id', 'rsid', 'transcript', 'effect', 'exon', 'interpro_domain', 'ref', 'alt', 'maf_exac', 'maf_1000g', 'maf_esp6500', 'dann', 'fathmm', 'metasvm', 'gerp++', 'dbscSNV_rf_score', 'dbscSNV_ada_score', 'clinvar_pathogenicity']) 

  # df_final_res.to_csv('result/variants.txt', sep = '\t', index = False)
  return final_res, variants
