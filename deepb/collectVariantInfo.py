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
import MySQLdb
import os.path
BASE = os.path.dirname(os.path.abspath(__file__))


reload(sys)
sys.setdefaultencoding('utf-8')
pd.options.display.max_colwidth = 10000

PARSED_CLINVAR = os.path.join(BASE, 'data/parsed_clinvar.txt')

## Collect information from myvariant 

def convertAminoAcidLowertoCap1letter(protein):
  global robj_amino_acid
  protein = protein.lower()
  protein = robj_amino_acid.sub(lambda m: amino_acid_mapping.mapl2u[m.group(0)], protein)
  return protein

def collectAll(gene, variant, transcript):
  mv = myvariant.MyVariantInfo()
  attempt, max_attempts = 0, 3
  while True:
    attempt += 1    
    if attempt > max_attempts:
      break
    try:
      snpeff = mv.query('snpeff.ann.gene_id:%s AND snpeff.ann.hgvs_c:%s'
           % (gene, variant), fields='snpeff')
      break
    except:
      time.sleep(random.uniform(0.3, 0.5))
      pass

  try:
    variant_id = snpeff['hits'][0]['_id']
  except (KeyError, IndexError):
    time.sleep(random.uniform(0.1, 0.3))
    snpeff = mv.query('snpeff.ann.gene_id:%s AND snpeff.ann.hgvs_c:%s'
                       % (gene, variant), fields='snpeff')
    try:
      variant_id = snpeff['hits'][0]['_id']
    except (KeyError, IndexError):
      return ''
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
  return variant_id

def collectSnpeff(gene, variant, transcript):
  try:
    ann = non_snpeff['snpeff']['ann']
  except KeyError:
    return '', ''
  if not isinstance(ann, list):
    effect = ann['effect'] if 'effect' in ann else ''
    protein = ann['hgvs_p'] if 'hgvs_p' in ann else ''
  else:
    transcript = transcript.decode('utf-8')
    effect = ann[0]['effect'] if 'effect' in ann[0] else ''
    protein = ann[0]['hgvs_p'] if 'hgvs_p' in ann[0] else ''
    max_similarity = 0
    for var in ann:
      if var['gene_id'] == gene and var['hgvs_c'] == variant: 
        sim = Levenshtein.ratio(transcript, var['feature_id'])
        if sim > max_similarity:
          max_similarity = sim
          effect = var['effect'] if 'effect' in var else ''
          protein = var['hgvs_p'] if 'hgvs_p' in var else ''
  protein = convertAminoAcidLowertoCap1letter(protein) 
  return effect, protein

def collectSnpeffWithGeneVariantInfo():
  try:
    ann = non_snpeff['snpeff']['ann']
  except KeyError:
    return '', '', '', '', ''
  if isinstance(ann, list):
    ann = ann[0]
  gene = ann['gene_id'] if 'gene_id' in ann else ''
  variant = ann['hgvs_c'] if 'hgvs_c' in ann else ''
  protein = ann['hgvs_p'] if 'hgvs_p' in ann else ''
  transcript = ann['feature_id'] if 'feature_id' in ann else ''
  effect = ann['effect'] if 'effect' in ann else ''
  protein = convertAminoAcidLowertoCap1letter(protein)
  return gene, variant, protein, transcript, effect

def collectExAC():
  try:
    maf_exac = float(non_snpeff['exac']['ac']['ac_adj']) / float(non_snpeff['exac']['an']['an_adj'])
  except KeyError:
    maf_exac = '' 
  except TypeError:
    try:
      maf_exac = float(max(non_snpeff['exac']['ac']['ac_adj'])) / float(non_snpeff['exac']['an']['an_adj'])
    except ZeroDivisionError:
      maf_exac = '' 
  except ZeroDivisionError:
    maf_exac = '' 
  try:
    maf_exac_nontcga = float(non_snpeff['exac_nontcga']['ac']['ac_adj']) / float(non_snpeff['exac_nontcga']['an']['an_adj'])
  except KeyError:
    maf_exac_nontcga = '' 
  except TypeError:
    try:
      maf_exac_nontcga = float(max(non_snpeff['exac_nontcga']['ac']['ac_adj'])) / float(non_snpeff['exac_nontcga']['an']['an_adj'])
    except ZeroDivisionError:
      maf_exac_nontcga = ''
  except ZeroDivisionError:
    maf_exac_nontcga = '' 
  return str(maf_exac), str(maf_exac_nontcga)

def collectExACDetails_bak():
  try:
    exac_tot_ac, exac_tot_an = float(non_snpeff['exac']['ac']['ac_adj']), float(non_snpeff['exac']['an']['an_adj'])
    maf_exac_tot = exac_tot_ac / exac_tot_an
  except KeyError:
    exac_tot_ac, exac_tot_an, maf_exac_tot = '', '', ''
  except TypeError:
    try:
      exac_tot_ac, exac_tot_an = float(max(non_snpeff['exac']['ac']['ac_adj'])), float(non_snpeff['exac']['an']['an_adj'])
      maf_exac_tot = exac_tot_ac / exac_tot_an
    except ZeroDivisionError:
      exac_tot_ac, exac_tot_an, maf_exac_tot = '', '', ''
  except ZeroDivisionError:
    exac_tot_ac, exac_tot_an, maf_exac_tot = '', '', ''
  try:
    exac_afr_ac, exac_afr_an = float(non_snpeff['exac']['ac']['ac_afr']), float(non_snpeff['exac']['an']['an_afr'])
    maf_exac_afr = exac_afr_ac / exac_afr_an
  except KeyError:
    exac_afr_ac, exac_afr_an, maf_exac_afr = '', '', ''
  except TypeError:
    try:
      exac_afr_ac, exac_afr_an = float(max(non_snpeff['exac']['ac']['ac_afr'])), float(non_snpeff['exac']['an']['an_afr'])
      maf_exac_afr = exac_afr_ac / exac_afr_an
    except ZeroDivisionError:
      exac_afr_ac, exac_afr_an, maf_exac_afr = '', '', ''
  except ZeroDivisionError:
    exac_afr_ac, exac_afr_an, maf_exac_afr = '', '', ''
  try:
    exac_amr_ac, exac_amr_an = float(non_snpeff['exac']['ac']['ac_amr']), float(non_snpeff['exac']['an']['an_amr'])
    maf_exac_amr = exac_amr_ac / exac_amr_an
  except KeyError:
    exac_amr_ac, exac_amr_an, maf_exac_amr = '', '', ''
  except TypeError:
    try:
      exac_amr_ac, exac_amr_an = float(max(non_snpeff['exac']['ac']['ac_amr'])), float(non_snpeff['exac']['an']['an_amr'])
      maf_exac_amr = exac_amr_ac / exac_amr_an
    except ZeroDivisionError:
      exac_amr_ac, exac_amr_an, maf_exac_amr = '', '', ''
  except ZeroDivisionError:
    exac_amr_ac, exac_amr_an, maf_exac_amr = '', '', ''
  try:
    exac_eas_ac, exac_eas_an = float(non_snpeff['exac']['ac']['ac_eas']), float(non_snpeff['exac']['an']['an_eas'])
    maf_exac_eas = exac_eas_ac / exac_eas_an
  except KeyError:
    exac_eas_ac, exac_eas_an, maf_exac_eas = '', '', ''
  except TypeError:
    try:
      exac_eas_ac, exac_eas_an = float(max(non_snpeff['exac']['ac']['ac_eas'])), float(non_snpeff['exac']['an']['an_eas'])
      maf_exac_eas = exac_eas_ac / exac_eas_an
    except ZeroDivisionError:
      exac_eas_ac, exac_eas_an, maf_exac_eas = '', '', ''
  except ZeroDivisionError:
    exac_eas_ac, exac_eas_an, maf_exac_eas = '', '', ''
  try:
    exac_fin_ac, exac_fin_an = float(non_snpeff['exac']['ac']['ac_fin']), float(non_snpeff['exac']['an']['an_fin'])
    maf_exac_fin = exac_fin_ac / exac_fin_an
  except KeyError:
    exac_fin_ac, exac_fin_an, maf_exac_fin = '', '', ''
  except TypeError:
    try:
      exac_fin_ac, exac_fin_an = float(max(non_snpeff['exac']['ac']['ac_fin'])), float(non_snpeff['exac']['an']['an_fin'])
      maf_exac_fin = exac_fin_ac / exac_fin_an
    except ZeroDivisionError:
      exac_fin_ac, exac_fin_an, maf_exac_fin = '', '', ''
  except ZeroDivisionError:
    exac_fin_ac, exac_fin_an, maf_exac_fin = '', '', ''
  try:
    exac_nfe_ac, exac_nfe_an = float(non_snpeff['exac']['ac']['ac_nfe']), float(non_snpeff['exac']['an']['an_nfe'])
    maf_exac_nfe = exac_nfe_ac / exac_nfe_an
  except KeyError:
    exac_nfe_ac, exac_nfe_an, maf_exac_nfe = '', '', ''
  except TypeError:
    try:
      exac_nfe_ac, exac_nfe_an = float(max(non_snpeff['exac']['ac']['ac_nfe'])), float(non_snpeff['exac']['an']['an_nfe'])
      maf_exac_nfe = exac_nfe_ac / exac_nfe_an
    except ZeroDivisionError:
      exac_nfe_ac, exac_nfe_an, maf_exac_nfe = '', '', ''
  except ZeroDivisionError:
    exac_nfe_ac, exac_nfe_an, maf_exac_nfe = '', '', ''
  try:
    exac_oth_ac, exac_oth_an = float(non_snpeff['exac']['ac']['ac_oth']), float(non_snpeff['exac']['an']['an_oth'])
    maf_exac_oth = exac_oth_ac / exac_oth_an
  except KeyError:
    exac_oth_ac, exac_oth_an, maf_exac_oth = '', '', ''
  except TypeError:
    try:
      exac_oth_ac, exac_oth_an = float(max(non_snpeff['exac']['ac']['ac_oth'])), float(non_snpeff['exac']['an']['an_oth'])
      maf_exac_oth = exac_oth_ac / exac_oth_an
    except ZeroDivisionError:
      exac_oth_ac, exac_oth_an, maf_exac_oth = '', '', ''
  except ZeroDivisionError:
    exac_oth_ac, exac_oth_an, maf_exac_oth = '', '', ''
  try:
    exac_sas_ac, exac_sas_an = float(non_snpeff['exac']['ac']['ac_sas']), float(non_snpeff['exac']['an']['an_sas'])
    maf_exac_sas = exac_sas_ac / exac_sas_an
  except KeyError:
    exac_sas_ac, exac_sas_an, maf_exac_sas = '', '', ''
  except TypeError:
    try:
      exac_sas_ac, exac_sas_an = float(max(non_snpeff['exac']['ac']['ac_sas'])), float(non_snpeff['exac']['an']['an_sas'])
      maf_exac_sas = exac_sas_ac / exac_sas_an
    except ZeroDivisionError:
      exac_sas_ac, exac_sas_an, maf_exac_sas = '', '', ''
  except ZeroDivisionError:
    exac_sas_ac, exac_sas_an, maf_exac_sas = '', '', ''

  '''   
  try:
    exac_het_ac, exac_het_an = float(non_snpeff['exac']['ac']['ac_het']), float(non_snpeff['exac']['an']['an_het'])
    maf_exac_het = exac_het_ac / exac_het_an
  except KeyError:
    exac_het_ac, exac_het_an, maf_exac_het = '', '', ''
  except TypeError:
    try:
      exac_het_ac, exac_het_an = float(max(non_snpeff['exac']['ac']['ac_het'])), float(non_snpeff['exac']['an']['an_het'])
      maf_exac_het = exac_het_ac / exac_het_an
    except ZeroDivisionError:
      exac_het_ac, exac_het_an, maf_exac_het = '', '', ''
  except ZeroDivisionError:
    exac_het_ac, exac_het_an, maf_exac_het = '', '', ''
  '''   
  try:
    exac_hom_ac, exac_hom_an = float(non_snpeff['exac']['ac']['ac_hom']), float(non_snpeff['exac']['an']['an_adj'])
    maf_exac_hom = exac_hom_ac / exac_hom_an
  except KeyError:
    exac_hom_ac, exac_hom_an, maf_exac_hom = '', '', ''
  except TypeError:
    try:
      exac_hom_ac, exac_hom_an = float(max(non_snpeff['exac']['ac']['ac_hom'])), float(non_snpeff['exac']['an']['an_adj'])
      maf_exac_hom = exac_hom_ac / exac_hom_an
    except ZeroDivisionError:
      exac_hom_ac, exac_hom_an, maf_exac_hom = '', '', ''
  except ZeroDivisionError:
    exac_hom_ac, exac_hom_an, maf_exac_hom = '', '', '' 

  exac_details = ([str(exac_tot_ac), str(exac_tot_an), str(maf_exac_tot),
                   str(exac_afr_ac), str(exac_afr_an), str(maf_exac_afr),
                   str(exac_amr_ac), str(exac_amr_an), str(maf_exac_amr), 
                   str(exac_eas_ac), str(exac_eas_an), str(maf_exac_eas), 
                   str(exac_fin_ac), str(exac_fin_an), str(maf_exac_fin), 
                   str(exac_nfe_ac), str(exac_nfe_an), str(maf_exac_nfe), 
                   str(exac_oth_ac), str(exac_oth_an), str(maf_exac_oth), 
                   str(exac_sas_ac), str(exac_sas_an), str(maf_exac_sas), 
                   str(exac_hom_ac), str(maf_exac_hom)])

  return exac_details

def collectExACDetails():
  try:
    exac_tot_ac, exac_tot_an = int(non_snpeff['exac']['ac']['ac_adj']), int(non_snpeff['exac']['an']['an_adj'])
    maf_exac_tot = float(exac_tot_ac) / exac_tot_an
  except KeyError:
    exac_tot_ac, exac_tot_an, maf_exac_tot = '', '', ''
  except TypeError:
    try:
      exac_tot_ac, exac_tot_an = int(max(non_snpeff['exac']['ac']['ac_adj'])), int(non_snpeff['exac']['an']['an_adj'])
      maf_exac_tot = float(exac_tot_ac) / exac_tot_an
    except ZeroDivisionError:
      exac_tot_ac, exac_tot_an, maf_exac_tot = '', '', ''
  except ZeroDivisionError:
    exac_tot_ac, exac_tot_an, maf_exac_tot = '', '', ''
  try:
    exac_afr_ac, exac_afr_an = int(non_snpeff['exac']['ac']['ac_afr']), int(non_snpeff['exac']['an']['an_afr'])
    maf_exac_afr = float(exac_afr_ac) / exac_afr_an
  except KeyError:
    exac_afr_ac, exac_afr_an, maf_exac_afr = '', '', ''
  except TypeError:
    try:
      exac_afr_ac, exac_afr_an = int(max(non_snpeff['exac']['ac']['ac_afr'])), int(non_snpeff['exac']['an']['an_afr'])
      maf_exac_afr = float(exac_afr_ac) / exac_afr_an
    except ZeroDivisionError:
      exac_afr_ac, exac_afr_an, maf_exac_afr = '', '', ''
  except ZeroDivisionError:
    exac_afr_ac, exac_afr_an, maf_exac_afr = '', '', ''
  try:
    exac_amr_ac, exac_amr_an = int(non_snpeff['exac']['ac']['ac_amr']), int(non_snpeff['exac']['an']['an_amr'])
    maf_exac_amr = float(exac_amr_ac) / exac_amr_an
  except KeyError:
    exac_amr_ac, exac_amr_an, maf_exac_amr = '', '', ''
  except TypeError:
    try:
      exac_amr_ac, exac_amr_an = int(max(non_snpeff['exac']['ac']['ac_amr'])), int(non_snpeff['exac']['an']['an_amr'])
      maf_exac_amr = float(exac_amr_ac) / exac_amr_an
    except ZeroDivisionError:
      exac_amr_ac, exac_amr_an, maf_exac_amr = '', '', ''
  except ZeroDivisionError:
    exac_amr_ac, exac_amr_an, maf_exac_amr = '', '', ''
  try:
    exac_eas_ac, exac_eas_an = int(non_snpeff['exac']['ac']['ac_eas']), int(non_snpeff['exac']['an']['an_eas'])
    maf_exac_eas = float(exac_eas_ac) / exac_eas_an
  except KeyError:
    exac_eas_ac, exac_eas_an, maf_exac_eas = '', '', ''
  except TypeError:
    try:
      exac_eas_ac, exac_eas_an = int(max(non_snpeff['exac']['ac']['ac_eas'])), int(non_snpeff['exac']['an']['an_eas'])
      maf_exac_eas = float(exac_eas_ac) / exac_eas_an
    except ZeroDivisionError:
      exac_eas_ac, exac_eas_an, maf_exac_eas = '', '', ''
  except ZeroDivisionError:
    exac_eas_ac, exac_eas_an, maf_exac_eas = '', '', ''
  try:
    exac_fin_ac, exac_fin_an = int(non_snpeff['exac']['ac']['ac_fin']), int(non_snpeff['exac']['an']['an_fin'])
    maf_exac_fin = float(exac_fin_ac) / exac_fin_an
  except KeyError:
    exac_fin_ac, exac_fin_an, maf_exac_fin = '', '', ''
  except TypeError:
    try:
      exac_fin_ac, exac_fin_an = int(max(non_snpeff['exac']['ac']['ac_fin'])), int(non_snpeff['exac']['an']['an_fin'])
      maf_exac_fin = float(exac_fin_ac) / exac_fin_an
    except ZeroDivisionError:
      exac_fin_ac, exac_fin_an, maf_exac_fin = '', '', ''
  except ZeroDivisionError:
    exac_fin_ac, exac_fin_an, maf_exac_fin = '', '', ''
  try:
    exac_nfe_ac, exac_nfe_an = int(non_snpeff['exac']['ac']['ac_nfe']), int(non_snpeff['exac']['an']['an_nfe'])
    maf_exac_nfe = float(exac_nfe_ac) / exac_nfe_an
  except KeyError:
    exac_nfe_ac, exac_nfe_an, maf_exac_nfe = '', '', ''
  except TypeError:
    try:
      exac_nfe_ac, exac_nfe_an = int(max(non_snpeff['exac']['ac']['ac_nfe'])), int(non_snpeff['exac']['an']['an_nfe'])
      maf_exac_nfe = float(exac_nfe_ac) / exac_nfe_an
    except ZeroDivisionError:
      exac_nfe_ac, exac_nfe_an, maf_exac_nfe = '', '', ''
  except ZeroDivisionError:
    exac_nfe_ac, exac_nfe_an, maf_exac_nfe = '', '', ''
  try:
    exac_oth_ac, exac_oth_an = int(non_snpeff['exac']['ac']['ac_oth']), int(non_snpeff['exac']['an']['an_oth'])
    maf_exac_oth = float(exac_oth_ac) / exac_oth_an
  except KeyError:
    exac_oth_ac, exac_oth_an, maf_exac_oth = '', '', ''
  except TypeError:
    try:
      exac_oth_ac, exac_oth_an = int(max(non_snpeff['exac']['ac']['ac_oth'])), int(non_snpeff['exac']['an']['an_oth'])
      maf_exac_oth = float(exac_oth_ac) / exac_oth_an
    except ZeroDivisionError:
      exac_oth_ac, exac_oth_an, maf_exac_oth = '', '', ''
  except ZeroDivisionError:
    exac_oth_ac, exac_oth_an, maf_exac_oth = '', '', ''
  try:
    exac_sas_ac, exac_sas_an = int(non_snpeff['exac']['ac']['ac_sas']), int(non_snpeff['exac']['an']['an_sas'])
    maf_exac_sas = float(exac_sas_ac) / exac_sas_an
  except KeyError:
    exac_sas_ac, exac_sas_an, maf_exac_sas = '', '', ''
  except TypeError:
    try:
      exac_sas_ac, exac_sas_an = int(max(non_snpeff['exac']['ac']['ac_sas'])), int(non_snpeff['exac']['an']['an_sas'])
      maf_exac_sas = float(exac_sas_ac) / exac_sas_an
    except ZeroDivisionError:
      exac_sas_ac, exac_sas_an, maf_exac_sas = '', '', ''
  except ZeroDivisionError:
    exac_sas_ac, exac_sas_an, maf_exac_sas = '', '', ''

  '''   
  try:
    exac_het_ac, exac_het_an = float(non_snpeff['exac']['ac']['ac_het']), float(non_snpeff['exac']['an']['an_het'])
    maf_exac_het = exac_het_ac / exac_het_an
  except KeyError:
    exac_het_ac, exac_het_an, maf_exac_het = '', '', ''
  except TypeError:
    try:
      exac_het_ac, exac_het_an = float(max(non_snpeff['exac']['ac']['ac_het'])), float(non_snpeff['exac']['an']['an_het'])
      maf_exac_het = exac_het_ac / exac_het_an
    except ZeroDivisionError:
      exac_het_ac, exac_het_an, maf_exac_het = '', '', ''
  except ZeroDivisionError:
    exac_het_ac, exac_het_an, maf_exac_het = '', '', ''
  '''   
  try:
    exac_hom_ac, exac_hom_an = int(non_snpeff['exac']['ac']['ac_hom']), int(non_snpeff['exac']['an']['an_adj'])
    maf_exac_hom = float(exac_hom_ac) / exac_hom_an
  except KeyError:
    exac_hom_ac, exac_hom_an, maf_exac_hom = '', '', ''
  except TypeError:
    try:
      exac_hom_ac, exac_hom_an = int(max(non_snpeff['exac']['ac']['ac_hom'])), int(non_snpeff['exac']['an']['an_adj'])
      maf_exac_hom = float(exac_hom_ac) / exac_hom_an
    except ZeroDivisionError:
      exac_hom_ac, exac_hom_an, maf_exac_hom = '', '', ''
  except ZeroDivisionError:
    exac_hom_ac, exac_hom_an, maf_exac_hom = '', '', '' 

  exac_details = ([str(exac_tot_ac), str(exac_tot_an), str(maf_exac_tot),
                   str(exac_afr_ac), str(exac_afr_an), str(maf_exac_afr),
                   str(exac_amr_ac), str(exac_amr_an), str(maf_exac_amr), 
                   str(exac_eas_ac), str(exac_eas_an), str(maf_exac_eas), 
                   str(exac_fin_ac), str(exac_fin_an), str(maf_exac_fin), 
                   str(exac_nfe_ac), str(exac_nfe_an), str(maf_exac_nfe), 
                   str(exac_oth_ac), str(exac_oth_an), str(maf_exac_oth), 
                   str(exac_sas_ac), str(exac_sas_an), str(maf_exac_sas), 
                   str(exac_hom_ac), str(maf_exac_hom)])

  return exac_details

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

def getClinvarData(genes, gene_variants):
  global PARSED_CLINVAR
  clinvar_pathogenicity, clinvar_pmids, clinvar_variation_ids, clinvar_review_status, clinvar_diseases = dict(), dict(), dict(), dict(), dict()
  #pathos= []
  with open(PARSED_CLINVAR, 'rU') as f:
    f.readline()
    for line in f:
      line = line.rstrip('\n')
      parts = line.split('\t')
      gene, variant, pathogenicity, records, variation_id, review_status, diseases = parts[3], parts[5], parts[10], parts[11], parts[12], parts[9], parts[7]
      if gene not in genes:
        continue
      splitted_records = records.split(' ||| ')
      description_from_each_submitter = []
      pathogenicity_from_each_submitter = []
      for record in splitted_records:
        assertionID, submitter, datelastevaluated, reviewstatus_, description_, assertionmethod, origin, species, method, citations, comment_, supporting_obs = record.split(' || ')
        description_ = description_.lower()
        if description_ == 'pathologic':
          description_ = 'pathogenic'
        pathogenicity_from_each_submitter.append((description_, submitter, datelastevaluated, method, comment_))
      #pathos.append(pathogenicity)
      pmids = re.findall(r'PubMed : [0-9]{1,20}', records)
      pmids = [_.split(' : ')[1] for _ in pmids]
      variants = variant.split('|')
      variants = [item for item in variants if item]
      for variant in variants:
        if (gene, variant) not in gene_variants:
          continue
        if (gene, variant) not in clinvar_pathogenicity:
          clinvar_pathogenicity[(gene, variant)] = [pathogenicity_from_each_submitter]
          clinvar_pmids[(gene, variant)] = pmids
          clinvar_variation_ids[(gene, variant)] = [variation_id]
          clinvar_review_status[(gene, variant)] = [review_status]
          clinvar_diseases[(gene, variant)] = [diseases]
        else:
          clinvar_pathogenicity[(gene, variant)].append(pathogenicity_from_each_submitter)
          clinvar_pmids[(gene, variant)] += pmids
          clinvar_variation_ids[(gene, variant)].append(variation_id)
          clinvar_review_status[(gene, variant)].append(review_status)
          clinvar_diseases[(gene, variant)].append(diseases)
    for key in clinvar_pathogenicity:
      values = clinvar_pathogenicity[key]
      merged_values = []
      for value in values:
        merged_values += value 
      clinvar_pathogenicity[key] = merged_values # list of tuples
    for key in clinvar_pmids:
      values = list(set(clinvar_pmids[key]))
      clinvar_pmids[key] = values
    for key in clinvar_variation_ids:
      values = list(set(clinvar_variation_ids[key]))
      values = '|'.join(values)
      clinvar_variation_ids[key] = values
    for key in clinvar_review_status:
      values = list(set(clinvar_review_status[key]))
      values = '|'.join(values)
      clinvar_review_status[key] = values
    for key in clinvar_diseases:
      values = list(set(clinvar_diseases[key]))
      values = [value for value in values if not re.match(r'not provided', value, re.I)] 
      values = '|'.join(values)
      clinvar_diseases[key] = values
    #print set(pathos)
  return clinvar_pathogenicity, clinvar_pmids, clinvar_variation_ids, clinvar_review_status, clinvar_diseases

def getClinvarDataBak(genes, gene_variants):
  global PARSED_CLINVAR
  clinvar_pathogenicity, clinvar_pmids, clinvar_variation_ids, clinvar_review_status = dict(), dict(), dict(), dict()
  #pathos= []
  with open(PARSED_CLINVAR, 'rU') as f:
    f.readline()
    for line in f:
      line = line.rstrip('\n')
      parts = line.split('\t')
      gene, variant, pathogenicity, records, variation_id, review_status = parts[3], parts[5], parts[10], parts[11], parts[12], parts[9]
      if gene not in genes:
        continue
      #pathos.append(pathogenicity)
      pmids = re.findall(r'PubMed : [0-9]{1,20}', records)
      pmids = [_.split(' : ')[1] for _ in pmids]
      variants = variant.split('|')
      variants = [item for item in variants if item]
      for variant in variants:
        if (gene, variant) not in gene_variants:
          continue
        if (gene, variant) not in clinvar_pathogenicity:
          clinvar_pathogenicity[(gene, variant)] = [pathogenicity]
          clinvar_pmids[(gene, variant)] = pmids
          clinvar_variation_ids[(gene, variant)] = [variation_id]
          clinvar_review_status[(gene, variant)] = [review_status]
        else:
          clinvar_pathogenicity[(gene, variant)].append(pathogenicity)
          clinvar_pmids[(gene, variant)] += pmids
          clinvar_variation_ids[(gene, variant)].append(variation_id)
          clinvar_review_status[(gene, variant)].append(review_status)
    for key in clinvar_pathogenicity:
      values = clinvar_pathogenicity[key]
      values = '|'.join(values)
      clinvar_pathogenicity[key] = values
    for key in clinvar_pmids:
      values = list(set(clinvar_pmids[key]))
      clinvar_pmids[key] = values
    for key in clinvar_variation_ids:
      values = list(set(clinvar_variation_ids[key]))
      values = '|'.join(values)
      clinvar_variation_ids[key] = values
    for key in clinvar_review_status:
      values = list(set(clinvar_review_status[key]))
      values = '|'.join(values)
      clinvar_review_status[key] = values
    #print set(pathos)
  return clinvar_pathogenicity, clinvar_pmids, clinvar_variation_ids, clinvar_review_status



def getVariantidfromDB(candidate_vars):
  db = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="Tianqi12",
                     db="DB_offline")
  query = 'select gene, variant, protein, transcript, variant_id, effect from genevariantproteinmapping where '
  for var in candidate_vars:
    gene, variant, transcript, variant_id, zygosity = var
    query += "(gene='%s' and variant='%s' and transcript='%s') or " % (gene, variant, transcript)    
  query = query[0:-4]
  cursor = db.cursor()
  cursor.execute(query)
  data = cursor.fetchall()
  db.close()
  res = dict() 
  for line in data:
    gene, variant, protein, transcript, variant_id, effect = line
    res[(gene, variant)] = variant_id 
  return res

def get_variants(candidate_vars):
  mv = myvariant.MyVariantInfo()
  variantidfromDB = getVariantidfromDB(candidate_vars)

  variant_ids = []
  variant_id2key = dict()
  variants = defaultdict(dict)

  # The dbscsnv (splicing effect prediction) can not be obtained from myvariant; instead, we have local flat dbscsnv files
  dbscsnv_chromosomes, dbscsnv_variants = [], {}
  # dict which records zygosity for each variant id
  variantid_zygosity = dict()
  for var in candidate_vars:
    #print var
    gene, variant, transcript, variant_id, zygosity = var
    key = (gene, variant)
    if not variant_id:
      if key in variantidfromDB.keys():
        variant_id = variantidfromDB[key]
      else:
        variant_id = collectAll(gene, variant, transcript)
    variantid_zygosity[variant_id] = zygosity
    variants[key]['gene'], variants[key]['variant'], variants[key]['transcript'], variants[key]['id'], variants[key]['zygosity'] = gene, variant, transcript, variant_id, zygosity
  
    # Only 'interpro_domain' is a list; all the other fields are strings 
    if not variant_id:
      variants[key]['maf_exac'] = variants[key]['maf_1000g'] = variants[key]['maf_esp6500'] = variants[key]['dann'] = variants[key]['fathmm'] = variants[key]['metasvm'] = variants[key]['gerp++'] = variants[key]['exon'] = variants[key]['ref'] = variants[key]['alt'] = variants[key]['rsid'] = ''
      variants[key]['interpro_domain'] = []
      variants[key]['clinvar_pathogenicity'], variants[key]['clinvar_pmids'], variants[key]['clinvar_variation_ids'], variants[key]['clinvar_review_status'] = [], [], '', ''
      variants[key]['clinvar_associated_diseases'] = ''
      variants[key]['effect'], variants[key]['protein']  = '', ''
      continue
    variant_ids.append(variant_id)
    if variant_id in variant_id2key:
      variant_id2key[variant_id].append((gene, variant, transcript))
    else:
      variant_id2key[variant_id] = [(gene, variant, transcript)]
    time.sleep(random.uniform(0.02, 0.1))

  variant_ids = list(set(variant_ids))
  #print variant_ids
  non_snpeff_var_data = []
  batch_size = 100
  start, end = 0, 0
  num_variant_ids = len(variant_ids)
  while True:
    start = end
    end += batch_size
    end = min(end, num_variant_ids)
    attempt, max_attempts = 0, 3
    while True:
      attempt += 1
      if attempt > max_attempts:
        break
      try:
        tmp = mv.getvariants(variant_ids[start:end], fields = ['exac.ac','exac.an', 'exac_nontcga.ac.ac_adj', 'exac_nontcga.an.an_adj',
                               'dbnsfp', 'cadd.1000g.af', 'cadd.esp.af', 'clinvar.omim', 'clinvar.rcv',
                               'cadd.annotype', 'cadd.consequence', 'cadd.consdetail', 'cadd.grantham',
                               'cadd.phred', 'cadd.exon', 'vcf.ref', 'vcf.alt', 'dbsnp.rsid',
                               'snpeff.ann.effect', 'snpeff.ann.gene_id', 'snpeff.ann.hgvs_p', 'snpeff.ann.hgvs_c', 'snpeff.ann.feature_id'])
        break
      except:
        time.sleep(random.uniform(0.3, 0.5))
        pass
    non_snpeff_var_data += tmp
    if end >= num_variant_ids:
      break

  global non_snpeff, robj_amino_acid
  robj_amino_acid = re.compile('|'.join(amino_acid_mapping.mapl2u.keys()))

  for data in non_snpeff_var_data:
    non_snpeff = data
    if "_id" not in non_snpeff:
      continue
    variant_id = non_snpeff['_id'] 
    keys = variant_id2key[variant_id]
    for key in keys:
      gene, variant, transcript = key
      key = (gene, variant)

      effect, protein = collectSnpeff(gene, variant, transcript)  
      variants[key]['effect'] = effect
      variants[key]['protein'] = protein

      maf_exac, maf_exac_nontcga = collectExAC()
      maf_exac = maf_exac_nontcga if not maf_exac and maf_exac_nontcga else maf_exac

      dbnsfp_exac, dbnsfp_1000g, cadd_1000g, cadd_esp = collectMAF()
      variants[key]['maf_exac'] = dbnsfp_exac if dbnsfp_exac else maf_exac
      variants[key]['maf_1000g'] = dbnsfp_1000g if dbnsfp_1000g else cadd_1000g
      variants[key]['maf_esp6500'] = cadd_esp

      # exac_details is a list which contails detailed exac data like race or
      # het/hom
      exac_details = collectExACDetails()
      variants[key]['exac_details'] = exac_details 

      pathogenicity_scores, interpro_domain = collectdbNSFP()
      dann, fathmm, metasvm, gerp = pathogenicity_scores 
      variants[key]['dann'], variants[key]['fathmm'], variants[key]['metasvm'], variants[key]['gerp++'] = dann, fathmm, metasvm, gerp
      variants[key]['interpro_domain'] = interpro_domain

      #clinvar_data = collectClinvar()
      #variants[key]['clinvar_pathogenicity'] = clinvar_data
      variants[key]['clinvar_pathogenicity'] = [] 
      variants[key]['clinvar_pmids'] = []
      variants[key]['clinvar_variation_ids'] = ''
      variants[key]['clinvar_review_status'] = ''
      variants[key]['clinvar_associated_diseases'] = ''

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
    with open(os.path.join(BASE, ('data/dbscSNV/dbscSNV1.1.' + chromosome)), 'rb') as f:
      f.readline()
      for line in f:
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
  genes = [var[0] for var in candidate_vars]
  gene_variants = [(var[0], var[1]) for var in candidate_vars]
  clinvar_pathogenicity, clinvar_pmids, clinvar_variation_ids, clinvar_review_status, clinvar_diseases = getClinvarData(genes, gene_variants)
  for key in variants.keys():
    if key in clinvar_pathogenicity:
      variants[key]['clinvar_pathogenicity'] = clinvar_pathogenicity[key]
    if key in clinvar_pmids:
      variants[key]['clinvar_pmids'] = clinvar_pmids[key]
    if key in clinvar_variation_ids:
      variants[key]['clinvar_variation_ids'] = clinvar_variation_ids[key]
    if key in clinvar_review_status:
      variants[key]['clinvar_review_status'] = clinvar_review_status[key]
    if key in clinvar_diseases:
      variants[key]['clinvar_associated_diseases'] = clinvar_diseases[key]

  print variants
  # pickle.dump(variants, open('result/variants.p', 'wb'))

  final_res = []
  for key in variants:
    print key
    v = variants[key]
    # final_res.append([v['gene'], v['variant'], v['protein'], v['id'], v['rsid'], v['transcript'], v['effect'], v['exon'], v['interpro_domain'], v['ref'], v['alt'], v['maf_exac'], v['maf_1000g'], v['maf_esp6500'], v['dann'], v['fathmm'], v['metasvm'], v['gerp++'], v['dbscSNV_rf_score'], v['dbscSNV_ada_score'], v['clinvar_pathogenicity']])
    final_res.append((v['gene'], v['variant'], v['protein']))
  # df_final_res = pd.DataFrame(final_res, columns = ['gene', 'variant', 'protein', 'id', 'rsid', 'transcript', 'effect', 'exon', 'interpro_domain', 'ref', 'alt', 'maf_exac', 'maf_1000g', 'maf_esp6500', 'dann', 'fathmm', 'metasvm', 'gerp++', 'dbscSNV_rf_score', 'dbscSNV_ada_score', 'clinvar_pathogenicity']) 

  # df_final_res.to_csv('result/variants.txt', sep = '\t', index = False)
  return final_res, variants


def get_variants_from_vcf(candidate_vars, variantid_zygosity):
  # if the input file is VCF, then candidate_vars do not contain gene symbol information; they only have variant ids; need to query gene, variant, transcript information from myvariant
  mv = myvariant.MyVariantInfo()

  variant_ids = []
  variants = defaultdict(dict)

  # The dbscsnv (splicing effect prediction) can not be obtained from myvariant; instead, we have local flat dbscsnv files
  dbscsnv_chromosomes, dbscsnv_variants = [], {}
  tmp_candidate_vars = []
  for var in candidate_vars:
    variant_ids.append(var[3])

  variant_ids = list(set(variant_ids))
  non_snpeff_var_data = []
  batch_size = 100
  start, end = 0, 0
  num_variant_ids = len(variant_ids)
  while True:
    start = end
    end += batch_size
    end = min(end, num_variant_ids)
    attempt, max_attempts = 0, 3
    while True:
      attempt += 1
      if attempt > max_attempts:
        break
      try:
        tmp = mv.getvariants(variant_ids[start:end], fields = ['exac.ac','exac.an', 'exac_nontcga.ac.ac_adj', 'exac_nontcga.an.an_adj',
                               'dbnsfp', 'cadd.1000g.af', 'cadd.esp.af', 'clinvar.omim', 'clinvar.rcv',
                               'cadd.annotype', 'cadd.consequence', 'cadd.consdetail', 'cadd.grantham',
                               'cadd.phred', 'cadd.exon', 'vcf.ref', 'vcf.alt', 'dbsnp.rsid',
                               'snpeff.ann.effect', 'snpeff.ann.gene_id', 'snpeff.ann.hgvs_p', 'snpeff.ann.hgvs_c', 'snpeff.ann.feature_id'])
        break
      except:
        time.sleep(random.uniform(0.3, 0.5))
        pass 
    non_snpeff_var_data += tmp
    if end >= num_variant_ids:
      break

  global non_snpeff, robj_amino_acid
  robj_amino_acid = re.compile('|'.join(amino_acid_mapping.mapl2u.keys()))
    
  for data in non_snpeff_var_data:
    non_snpeff = data
    try:
      variant_id = non_snpeff['_id'] 
    except KeyError:
      continue
    gene, variant, protein, transcript, effect = collectSnpeffWithGeneVariantInfo()
    zygosity = variantid_zygosity[variant_id]
    if not gene:
      continue
    key = (gene, variant)
    variants[key]['id'] = variant_id 
    variants[key]['gene'] = gene 
    variants[key]['variant'] = variant 
    variants[key]['protein'] = protein
    variants[key]['transcript'] = transcript 
    variants[key]['effect'] = effect
    variants[key]['zygosity'] = zygosity 

    tmp_candidate_vars.append((gene, variant, transcript, variant_id, zygosity))

    maf_exac, maf_exac_nontcga = collectExAC()
    maf_exac = maf_exac_nontcga if not maf_exac and maf_exac_nontcga else maf_exac

    dbnsfp_exac, dbnsfp_1000g, cadd_1000g, cadd_esp = collectMAF()
    variants[key]['maf_exac'] = dbnsfp_exac if dbnsfp_exac else maf_exac
    variants[key]['maf_1000g'] = dbnsfp_1000g if dbnsfp_1000g else cadd_1000g
    variants[key]['maf_esp6500'] = cadd_esp

    # exac_details is a list which contails detailed exac data like race or
    # het/hom
    exac_details = collectExACDetails()
    variants[key]['exac_details'] = exac_details

    pathogenicity_scores, interpro_domain = collectdbNSFP()
    dann, fathmm, metasvm, gerp = pathogenicity_scores 
    variants[key]['dann'], variants[key]['fathmm'], variants[key]['metasvm'], variants[key]['gerp++'] = dann, fathmm, metasvm, gerp
    variants[key]['interpro_domain'] = interpro_domain

    #clinvar_data = collectClinvar()
    variants[key]['clinvar_pathogenicity'] = [] 
    variants[key]['clinvar_pmids'] = []
    variants[key]['clinvar_variation_ids'] = ''
    variants[key]['clinvar_review_status'] = ''
    variants[key]['clinvar_associated_diseases'] = ''

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
  for chromosome in set(dbscsnv_chromosomes):
    with open(os.path.join(BASE, ('data/dbscSNV/dbscSNV1.1.' + chromosome)), 'rb') as f:
      f.readline()
      for line in f:
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
  ## The old candidate_vars form vcf file only contains variant_id, the other records are '', so it is updated
  candidate_vars = tmp_candidate_vars
  genes = [var[0] for var in candidate_vars]
  gene_variants = [(var[0], var[1]) for var in candidate_vars]
  clinvar_pathogenicity, clinvar_pmids, clinvar_variation_ids, clinvar_review_status, clinvar_diseases = getClinvarData(genes, gene_variants)
  for key in variants.keys():
    if key in clinvar_pathogenicity:
      variants[key]['clinvar_pathogenicity'] = clinvar_pathogenicity[key]
    if key in clinvar_pmids:
      variants[key]['clinvar_pmids'] = clinvar_pmids[key]
    if key in clinvar_variation_ids:
      variants[key]['clinvar_variation_ids'] = clinvar_variation_ids[key]
    if key in clinvar_review_status:
      variants[key]['clinvar_review_status'] = clinvar_review_status[key]
    if key in clinvar_diseases:
      variants[key]['clinvar_associated_diseases'] = clinvar_diseases[key]

  final_res = []
  for key in variants:
    v = variants[key]
    final_res.append((v['gene'], v['variant'], v['protein']))

  return final_res, variants, candidate_vars

