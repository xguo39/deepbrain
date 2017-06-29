# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re
import amino_acid_mapping
import sys
import MySQLdb
import pickle
import time
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from pattern.en import pluralize, singularize
from collections import Counter
import os
BASE = os.path.dirname(os.path.abspath(__file__))

reload(sys)
sys.setdefaultencoding("utf-8")

def getTopVariantsFromACMGRankings(ACMG_result):
    variantsdata= dict()
    top_variants = []
    for index, row in ACMG_result.iterrows():
        gene, variant, id, final_score, pathogenicity_score, pathogenicity, hit_criteria, hpo_hit_score = row['gene'], row['variant'], row['id'], row['final_score'], row['pathogenicity_score'], row['pathogenicity'], row['hit_criteria'], row['hpo_hit_score']
        top_variants.append((gene, variant))
        variantsdata[(gene, variant)] = [id, final_score, pathogenicity_score, pathogenicity, hit_criteria, hpo_hit_score]

    return top_variants, variantsdata

def getProteinDomainOfTopVariants(variants, top_variants):
    protein_domains, proteins = dict(), dict()
    for var in top_variants:
        protein_domains[var] = variants[var]['interpro_domain']
        proteins[var] = variants[var]['protein']
    return protein_domains, proteins

# Update top variants and protein domains key by adding protein to the key: (gene, variant) --> (gene, variant, protein)
def updateTopVariantsAndProteinDomainsKey(top_variants, protein_domains, proteins, variantsdata):
    updated_top_variants, updated_protein_domains, updated_variantsdata = [], dict(), dict()
    for key in top_variants:
        gene, variant = key
        protein = proteins[key]
        updated_top_variants.append((gene, variant, protein))
    for key in protein_domains.keys():
        gene, variant = key
        protein = proteins[key]
        updated_protein_domains[(gene, variant, protein)] = protein_domains[key]
    for key in variantsdata.keys():
        gene, variant = key
        protein = proteins[key]
        updated_variantsdata[(gene, variant, protein)] = variantsdata[key]
    variantsdata = updated_variantsdata
    return updated_top_variants, updated_protein_domains, variantsdata

def searchSimilarProteinDomain(gene, protein_domain, dbdata):
    re_domain = re.compile(r'(' +'|'.join(protein_domain) + r')') 
    similar_variants = []
    for line in dbdata:
        dbgene, variant, protein, domain = line
        if dbgene != gene:
            continue
        if re_domain.search(domain):
            similar_variants.append((dbgene, variant, protein))
    return similar_variants

def queryVariantsInSameProteinDomain(protein_domains): 

    db = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="Tianqi12",
                     db="DB_offline")

    genes = [var[0] for var in protein_domains.keys()]
    genes = '(' +', '.join("'" + item + "'" for item in genes) + ')'
    query = "select d.gene, m.variant, m.protein, d.protein_domains from var2proteindomains d, genevariantproteinmapping m where d.gene in %s and d.gene = m.gene and (d.protein_variant = m.variant or d.protein_variant = m.protein)" % genes
    cursor = db.cursor()
    cursor.execute(query)
    dbdata = cursor.fetchall()
    db.close()

    samedomainvariants, domainvariants2original = dict(), dict() 
    for var in protein_domains.keys():
	gene, variant, protein = var
	protein_domain = protein_domains[var]
	samedomainvariants[(gene, variant, protein)] = [(gene, variant, protein)]
	if not protein_domain:
	    continue
	tmp_protein_domain = []
	for domain in protein_domain:
	    if '|' in domain:
		tmp_protein_domain += domain.split('|')
	    else:
		tmp_protein_domain.append(domain)
	protein_domain = list(set(tmp_protein_domain))
        similar_variants = searchSimilarProteinDomain(gene, protein_domain, dbdata) 
        samedomainvariants[(gene, variant, protein)] += similar_variants
    for key in samedomainvariants.keys():
        samedomainvariants[key] = list(set(samedomainvariants[key]))
    for key in samedomainvariants.keys():
        gene, variant, protein = key
        similar_variants = ', '.join(['|'.join(var) for var in samedomainvariants[key] if var[1] != variant])
        if not similar_variants:
            continue
        if (gene, variant) in curr_interpret:
            curr_interpret[(gene, variant)].append('Similar genetic variants that affect the same protein domain were identified: %s.' % similar_variants)
            curr_interpret_chinese[(gene, variant)].append('与此基因变异相似，影响相同蛋白功能区的变异包括: %s.' % similar_variants)
        else:
            curr_interpret[(gene, variant)] = ['Similar genetic variants that affect the same protein domain were identified: %s.' % similar_variants]
            curr_interpret_chinese[(gene, variant)] = ['与此基因变异相似，影响相同蛋白功能区的变异包括: %s.' % similar_variants]
    for key in samedomainvariants.keys():
        values = samedomainvariants[key]
        for value in values:
            if value not in samedomainvariants.keys():
                domainvariants2original[value] = key
            else:
                domainvariants2original[value] = value
    return samedomainvariants, domainvariants2original 

def queryPhenosFromDB(samedomainvariants, domainvariants2original):
    db = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="Tianqi12",
                     db="DB_offline")

    variantphenos = dict() 
    query = "select gene, protein_variant, phenotypes from var2phenos where "
    for key in samedomainvariants.keys():
        variants = samedomainvariants[key]
        for var in variants:
            gene, variant, protein = var
            if protein:
                query += "(gene = '%s' and (protein_variant = '%s' or protein_variant = '%s')) or " % (gene, variant, protein)
            else:
                query += "(gene = '%s' and protein_variant = '%s') or " % (gene, variant)
    query = query[0:-4]
    cursor = db.cursor()
    cursor.execute(query)
    dbdata = cursor.fetchall()
    db.close()
    for key in samedomainvariants.keys():
        samedomainvariant_list = samedomainvariants[key]
        for samedomainvar in samedomainvariant_list:
            gene_, variant, protein = samedomainvar
	    for data in dbdata:
		gene, protein_variant, pheno = data 
		if gene == gene_ and protein_variant in [variant, protein]:
                    originalvar = domainvariants2original[(gene, variant, protein)]
		    if originalvar in variantphenos:
			variantphenos[originalvar] += pheno.split('|')
		    else:
			variantphenos[originalvar] = pheno.split('|')
    for key in variantphenos.keys():
        value = list(set(variantphenos[key]))
        variantphenos[key] = value 
    return variantphenos

def searchPhenosFromDBdata(patient_phenotypes, variantphenos):
    re_pheno = re.compile(r'(' +'|'.join(patient_phenotypes) + r')', re.I)
    variantphenosfromDB = dict()
    for key in variantphenos.keys():
        phenos = ' '.join(variantphenos[key])
        if not re_pheno.search(phenos):
            continue
        else:
	    if key in variantphenosfromDB:
		variantphenosfromDB[key] += re_pheno.findall(phenos) 
	    else:
		variantphenosfromDB[key] = re_pheno.findall(phenos) 

    #************ New lines
    for key in variantphenosfromDB.keys():
        gene, variant, protein = key
        phenos = list(set(variantphenosfromDB[key])) 
        if (gene, variant) in curr_interpret:
            curr_interpret[(gene, variant)].append("We find variants that affect the same protein domain as our case may lead to the phenos that match our patient's from genomic databases (OMIM, ORPHANET, etc): %s." % (', '.join(list(set(phenos))))) 
            curr_interpret_chinese[(gene, variant)].append("基因疾病数据库(比如OMIM, ORPHANET)中报道与此基因变异类似、影响相同蛋白功能区的变异可能导致的如下表型与该病人吻合: %s." % (', '.join(list(set(phenos))))) 
        else:
            curr_interpret[(gene, variant)] = ["We find variants that affect the same protein domain as our case may lead to the phenos that match our patient's from genomic databases (OMIM, ORPHANET, etc): %s." % (', '.join(list(set(phenos))))]
            curr_interpret_chinese[(gene, variant)] = ["基因疾病数据库(比如OMIM, ORPHANET)中报道与此基因变异类似、影响相同蛋白功能区的变异可能导致的如下表型与该病人吻合: %s." % (', '.join(list(set(phenos))))]
    return variantphenosfromDB

def initWordDifficultyIndex():
    global word_difficulty_index
    df = pd.read_csv(os.path.join(BASE, 'data/word_difficulty_index.txt'), usecols = [0, 1, 2])
    df['Word'] = df['Word'].str.lower()
    word_difficulty_index = df.set_index(['Word']).to_dict()['Freq_HAL']
    return word_difficulty_index

def searchPhenosFromPubmed(patient_phenotypes, samedomainvariants, domainvariants2original):
    global word_difficulty_index, patient_phenotypes_wordbreak
    db = MySQLdb.connect(host="localhost",
                 user="root",
                 passwd="Tianqi12",
                 db="DB_offline")
    variantphenosfromPubmed = dict()
    query = "select gene, protein_variant, pmid, title, abstract from pubmed_var where "
    for key in samedomainvariants.keys():
        variants = samedomainvariants[key]
        for var in variants:
            gene, variant, protein = var
            if protein:
                query += "(gene = '%s' and (protein_variant = '%s' or protein_variant = '%s')) or " % (gene, variant, protein)
            else:
                query += "(gene = '%s' and protein_variant = '%s') or " % (gene, variant)
    query = query[0:-4]
    cursor = db.cursor()
    cursor.execute(query)
    dbdata = cursor.fetchall()
    db.close()

    # break terms to word list: 'pulmonary hypoplasia' -> ['pulmonary', 'hypoplasia']
    patient_phenotypes_wordbreak = []
    for pheno in patient_phenotypes:
        pheno_wordlist = pheno.split()
        #pheno_wordlist = [singularize(word, custom={'toes':'toe'}) for word in pheno_wordlist]
        append_wordlist = False 
        for word in pheno_wordlist:
            word = word.lower()
            if word not in word_difficulty_index.keys() or word_difficulty_index[word] < 100:
                append_wordlist = True
                rare_words_in_pheno_wordlist = [word for word in pheno_wordlist if word not in word_difficulty_index or word_difficulty_index[word] < 1000]
                patient_phenotypes_wordbreak += rare_words_in_pheno_wordlist
                break   
        if not append_wordlist:
            patient_phenotypes_wordbreak.append(pheno)
    tmp_patient_phenotypes_wordbreak = []
    for pheno in patient_phenotypes_wordbreak:
        if pheno not in word_difficulty_index.keys() or word_difficulty_index[pheno] < 160000:
            tmp_patient_phenotypes_wordbreak.append(pheno)
    patient_phenotypes_wordbreak = tmp_patient_phenotypes_wordbreak 

    re_pubmed = re.compile(r'\b(' +'|'.join(patient_phenotypes_wordbreak) + r')', re.I)

    #************ New line
    variantphenospmids = dict()
    for data in dbdata:
        gene, protein_variant, pmid, title, abstract = data
        text = title + ' ' + abstract
        #text = singularize(text, custom={'toes':'toe'}) 
        for key in samedomainvariants.keys():
            samedomainvariant_list = samedomainvariants[key]
            processed_pmids_for_current_variant = []    
            for samedomainvar in samedomainvariant_list:
                gene_, variant, protein = samedomainvar 
                if gene == gene_ and protein_variant in [variant, protein]:
                    if pmid in processed_pmids_for_current_variant:
                        continue    
                    processed_pmids_for_current_variant.append(pmid)
                    if not re_pubmed.search(text):
			continue
                    originalvar = domainvariants2original[(gene, variant, protein)]
                    if originalvar in variantphenosfromPubmed:
                        variantphenosfromPubmed[originalvar] += re_pubmed.findall(text) 
                        #************ New line
                        variantphenospmids[originalvar].append(pmid)
                    else:
			variantphenosfromPubmed[originalvar] = re_pubmed.findall(text) 
                        #************ New line
                        variantphenospmids[originalvar] = [pmid]

    #************ New lines
    for key in variantphenospmids.keys():
        gene, variant, protein = key
        pmids = variantphenospmids[key]
        pmids = ["<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'> %s </a>" %(i,i) for i in pmids]
        if (gene, variant) in curr_interpret:
            curr_interpret[(gene, variant)].append('Previous literature (PMIDs: %s) reported similar phenotypes caused by genetic variants affecting the same protein domain as out current case.' % (', ').join(list(set(pmids))))
            curr_interpret_chinese[(gene, variant)].append('生物医学文献(PMIDs: %s)之前报道此基因变异的相似变异(影响相同蛋白功能区)引发与该病人相似的表型.' % (', ').join(list(set(pmids))))
        else:
            curr_interpret[(gene, variant)] = ['Previous literature (PMIDs: %s) reported similar phenotypes caused by genetic variants affecting the same protein domain as out current case.' % (', ').join(list(set(pmids)))]
            curr_interpret_chinese[(gene, variant)] = ['生物医学文献(PMIDs: %s)之前报道此基因变异的相似变异(影响相同蛋白功能区)引发与该病人相似的表型.' % (', ').join(list(set(pmids)))]
    return variantphenosfromPubmed

## Generate antonyms of a word using NLTK and wordnet
def get_antonyms(word):
    antonyms = []
    for synset in wn.synsets(word):
        for lemma in synset.lemmas():
            antonyms += lemma.antonyms()
            similar_synsets = synset.similar_tos()
            for similar_synset in similar_synsets:
                for lemma_ in similar_synset.lemmas():
                    antonyms += lemma_.antonyms()
    direct_antonyms = list(set(antonyms))
    # Get similar words of the direct antonyms
    for antonym in direct_antonyms:
        similar_synsets = antonym.synset().similar_tos()
        for synset in similar_synsets:
            for lemma in synset.lemmas():
                antonyms.append(lemma)
    antonyms = list(set(antonyms))
    antonyms = set([_.name() for _ in antonyms])
    return antonyms

# Use re for split hpo terms
# Use lemmatizer to lemmatize words e.g., disturbances --> distrubance
def isOppositeMeaning(words_in_pheno_only, words_in_hpo_only):
    global processed_antonyms
    # If any word ends with ness, convert to its noun form
    words_in_pheno_only |= set([_[0:-4] for _ in words_in_pheno_only if _.endswith('ness')])
    words_in_hpo_only |= set([_[0:-4] for _ in words_in_hpo_only if _.endswith('ness')])
    # corner case: gain
    if 'gain' in words_in_hpo_only:
        words_in_hpo_only.add('increased')
        words_in_hpo_only.add('steady')
    if 'gain' in words_in_pheno_only:
        words_in_pheno_only.add('increased')
        words_in_pheno_only.add('steady')
    # Poor weight gain and weight gain are in opposite meaning
    if (words_in_pheno_only == set(['poor']) and words_in_hpo_only == set()) or (words_in_hpo_only == set(['poor']) and words_in_pheno_only == set()):
        #print "Opposite meaning due to word 'poor'", words_in_pheno_only, words_in_hpo_only
        return True
    for word in words_in_pheno_only:
        try:
            if word in processed_antonyms:
                antonyms = processed_antonyms[word]
            else:
                #print "get antonyms for word:", word
                antonyms = get_antonyms(word)
                processed_antonyms[word] = antonyms
        except UnicodeDecodeError as e:
            continue
        if antonyms.intersection(words_in_hpo_only):
            #print "Opposite meaning: ", antonyms.intersection(words_in_hpo_only)
            return True
    for word in words_in_hpo_only:
        try:
            if word in processed_antonyms:
                antonyms = processed_antonyms[word]
            else:
                #print "get antonyms for word:", word
                antonyms = get_antonyms(word)
                processed_antonyms[word] = antonyms
        except UnicodeDecodeError as e:
            continue
        if antonyms.intersection(words_in_pheno_only):
            #print "Opposite meaning: ", antonyms.intersection(words_in_hpo_only)
            return True
    return False

def identifyVariantsWithOppositePhenos(variantphenos, patient_phenotypes):
    #print variantphenos # This is variant phenos from DB
    variants_with_opposite_phenos = dict()
    processed_variant_phenos = dict()
    for var in variantphenos.keys():
        phenos = variantphenos[var]
        processed_variant_phenos[var] = []
        for pheno in phenos:
            pheno = [_.strip(",()'") for _ in re.split(' |/', pheno)]
            try:
                var_pheno_wordlist = [lemmatizer.lemmatize(word) for word in pheno]
            except UnicodeDecodeError as e:
                pass
            processed_variant_phenos[var].append(var_pheno_wordlist) # dict of list of lists 
    for patient_pheno in patient_phenotypes:
        patient_pheno = [_.strip(",()'") for _ in re.split(' |/', patient_pheno)]
        try:
            patient_pheno_wordlist = [lemmatizer.lemmatize(word) for word in patient_pheno]
        except UnicodeDecodeError as e:
            pass
        for var in processed_variant_phenos.keys():
            phenos = processed_variant_phenos[var]
            for var_pheno_wordlist in phenos:
                if set(var_pheno_wordlist) == set(patient_pheno_wordlist):
                    continue
                common_words = set(var_pheno_wordlist) & set(patient_pheno_wordlist)
                if not common_words:
                    continue
                words_in_patient_pheno_only = set(patient_pheno_wordlist) - common_words
                words_in_var_pheno_only = set(var_pheno_wordlist) - common_words
                #*********** New line
                if words_in_patient_pheno_only and words_in_var_pheno_only and isOppositeMeaning(words_in_var_pheno_only, words_in_patient_pheno_only):
                    # print words_in_patient_pheno_only, words_in_var_pheno_only
                    if var in variants_with_opposite_phenos:
                        variants_with_opposite_phenos[var].append((' '.join(patient_pheno), ' '.join(var_pheno_wordlist)))
                    else:
                        variants_with_opposite_phenos[var] = [(' '.join(patient_pheno), ' '.join(var_pheno_wordlist))]
    for var in variants_with_opposite_phenos.keys():
        value = list(set(variants_with_opposite_phenos[var]))
        variants_with_opposite_phenos[var] = value
    return variants_with_opposite_phenos

def bakidentifyVariantsWithOppositePhenos(variantphenos, patient_phenotypes):
    #print variantphenos # This is variant phenos from DB
    variants_with_opposite_phenos = []
    processed_variant_phenos = dict()
    for var in variantphenos.keys():
        phenos = variantphenos[var]
        processed_variant_phenos[var] = [] 
        for pheno in phenos:
            pheno = [_.strip(",()'") for _ in re.split(' |/', pheno)]
            try:
                var_pheno_wordlist = [lemmatizer.lemmatize(word) for word in pheno] 
            except UnicodeDecodeError as e:
                pass
            processed_variant_phenos[var].append(var_pheno_wordlist) # dict of list of lists 
    for patient_pheno in patient_phenotypes:
        patient_pheno = [_.strip(",()'") for _ in re.split(' |/', patient_pheno)]
        try:
            patient_pheno_wordlist = [lemmatizer.lemmatize(word) for word in patient_pheno]
        except UnicodeDecodeError as e:
            pass
        for var in processed_variant_phenos.keys():   
            phenos = processed_variant_phenos[var]
            for var_pheno_wordlist in phenos:
                if set(var_pheno_wordlist) == set(patient_pheno_wordlist):
                    continue
                common_words = set(var_pheno_wordlist) & set(patient_pheno_wordlist)
                if not common_words:
                    continue
                words_in_patient_pheno_only = set(patient_pheno_wordlist) - common_words
                words_in_var_pheno_only = set(var_pheno_wordlist) - common_words
                #*********** New line
                if words_in_patient_pheno_only and words_in_var_pheno_only and isOppositeMeaning(words_in_var_pheno_only, words_in_patient_pheno_only): 
                    # print words_in_patient_pheno_only, words_in_var_pheno_only
                    variants_with_opposite_phenos.append(var) 
    return list(set(variants_with_opposite_phenos))

def getScores(variantphenosfromPubmed, variantphenosfromDB, variantphenos, patient_phenotypes):
    global patient_phenotypes_wordbreak, word_difficulty_index
    scores = dict()
    variantphenosfromPubmedAndDB = dict()
    #***** New lines (convert pubmed matched text to lower case)
    for originalvar in variantphenosfromPubmed.keys():
        values = variantphenosfromPubmed[originalvar]
        values = [value.lower() for value in values]
        variantphenosfromPubmed[originalvar] = values
    for originalvar in variantphenosfromPubmed.keys():
        variantphenosfromPubmedAndDB[originalvar] = variantphenosfromPubmed[originalvar]
    for originalvar in variantphenosfromDB.keys():
        if originalvar in variantphenosfromPubmedAndDB:
            variantphenosfromPubmedAndDB[originalvar] += variantphenosfromDB[originalvar]
        else:
            variantphenosfromPubmedAndDB[originalvar] = variantphenosfromDB[originalvar]
    #print 'variant phenos from Pubmed and DB are'
    #print variantphenosfromPubmedAndDB

    for originalvar in variantphenosfromPubmed.keys():
	items_count = Counter(variantphenosfromPubmed[originalvar])
	#print items_count
	for item in items_count.keys():
            item = item.lower()
            difficulty_index = word_difficulty_index[item] if item in word_difficulty_index else 50
            weight = 8.0 / np.log(difficulty_index) ## The more difficult the word, the more weight to be assigned
	    if originalvar in scores:
		scores[originalvar] += np.log( min((items_count[item] + 1), 10) ) * weight 
	    else:
		scores[originalvar] = np.log( min((items_count[item] + 1), 10) ) * weight 
    for originalvar in variantphenosfromDB.keys():
	items_count = Counter(variantphenosfromDB[originalvar])
	#print items_count
	for item in items_count.keys():
            item = item.lower()
            difficulty_index = word_difficulty_index[item] if item in word_difficulty_index else 50
            weight = 8.0 / np.log(difficulty_index) ## The more difficult the word, the more weight to be assigned
	    if originalvar in scores:
		scores[originalvar] += np.log( min((items_count[item] + 1), 10) ) * weight 
	    else:
		scores[originalvar] = np.log( min((items_count[item] + 1), 10) ) * weight 

    # print scores
    for originalvar in variantphenosfromPubmedAndDB.keys():
        num_match_phenos = float(len(set(variantphenosfromPubmedAndDB[originalvar])))        
        if originalvar in variantphenos.keys():
            num_all_var_phenos = len(variantphenos[originalvar])
        else:
            num_all_var_phenos = num_match_phenos 
        num_all_patient_phenos = len(patient_phenotypes_wordbreak)
        scores[originalvar] = 1.0 + np.sqrt(scores[originalvar]) * np.sqrt(num_match_phenos / num_all_var_phenos) * np.sqrt(num_match_phenos / num_all_patient_phenos)
    # print scores
   
    # Make sure the phenos associated with variants do not have conflicts with the patient's phenos
    global lemmatizer, processed_antonyms
    lemmatizer = WordNetLemmatizer()
    processed_antonyms = dict()
    variants_with_opposite_phenos = identifyVariantsWithOppositePhenos(variantphenos, patient_phenotypes)

    for originalvar in variants_with_opposite_phenos:
        #********* New line
        gene, variant, protein = originalvar
        #********* New line
        oppo_phenos = variants_with_opposite_phenos[originalvar]
        oppo_phenos = [' vs. '.join(pheno) for pheno in oppo_phenos]
        oppo_phenos = ', '.join(oppo_phenos)
        if (gene, variant) in curr_interpret:
            curr_interpret[(gene, variant)].append('We found previously reported cases that the genetic variants in the same protein domain as our case caused OPPOSITE phenotypes as our patient: %s.' % oppo_phenos)
            curr_interpret_chinese[(gene, variant)].append('基因疾病数据库(比如OMIM, ORPHANET)报道与此基因变异相似的变异引发与该病人相反的表型: %s. 该变异对此病人的致病权重应下调.' % oppo_phenos)
        else:
            curr_interpret[(gene, variant)] = ['We found previously reported cases that the genetic variants in the same protein domain as our case caused OPPOSITE phenotypes as our patient: %s.' % oppo_phenos]
            curr_interpret_chinese[(gene, variant)] = ['基因疾病数据库(比如OMIM, ORPHANET)报道与此基因变异相似的变异引发与该病人相反的表型: %s. 该变异对此病人的致病权重应下调.' % oppo_phenos]
        if originalvar in scores:
            scores[originalvar] = scores[originalvar] * 0.9
        else:
            scores[originalvar] = 1.0 * 0.9
    return scores

def generateOutput(variants, ACMG_result, patient_phenotypes, variant_ACMG_interpret, variant_ACMG_interpret_chinese): 
    global patient_phenotypes_wordbreak, curr_interpret, curr_interpret_chinese
    curr_interpret, curr_interpret_chinese = dict(), dict()

    top_variants, variantsdata = getTopVariantsFromACMGRankings(ACMG_result)
    protein_domains, proteins = getProteinDomainOfTopVariants(variants, top_variants)
    top_variants, protein_domains, variantsdata = updateTopVariantsAndProteinDomainsKey(top_variants, protein_domains, proteins, variantsdata) # Now key is (gene, variant, protein)
    samedomainvariants, domainvariants2original = queryVariantsInSameProteinDomain(protein_domains)
    variantphenos = queryPhenosFromDB(samedomainvariants, domainvariants2original)
    # print variantphenos
    variantphenosfromDB = searchPhenosFromDBdata(patient_phenotypes, variantphenos)
    initWordDifficultyIndex()
    variantphenosfromPubmed = searchPhenosFromPubmed(patient_phenotypes, samedomainvariants, domainvariants2original)
    scores = getScores(variantphenosfromPubmed, variantphenosfromDB, variantphenos, patient_phenotypes)

    final_res = []
    for key in variantsdata:
        gene, variant, protein = key
        id, final_score, pathogenicity_score, pathogenicity, hit_criteria, hpo_hit_score = variantsdata[key]
        pheno_match_score = scores[key] if key in scores else 1.0
        final_score = float(final_score) * pheno_match_score
        final_res.append([gene, variant, protein, id, final_score, pathogenicity, hit_criteria, pathogenicity_score, hpo_hit_score, pheno_match_score])	
    df_final_res = pd.DataFrame(final_res, columns = ['gene', 'variant', 'protein', 'id', 'final_score', 'pathogenicity', 'hit_criteria', 'pathogenicity_score', 'hpo_hit_score', 'pheno_match_score'])
    df_final_res['pheno_match_score'] = df_final_res['pheno_match_score']+0.03*df_final_res['hpo_hit_score']
    # df_final_res['pheno_match_score'] = df_final_res['hpo_hit_score']
    df_final_res['final_score'] = df_final_res['final_score'].apply(lambda x: round(x,2))
    df_final_res['pheno_match_score'] = df_final_res['pheno_match_score'].apply(lambda x: round(x,2))
    df_final_res.sort_values(by=['final_score'], ascending = [0], inplace = True)

    tmp_df_final_res = df_final_res.copy()
    tmp_df_final_res.drop_duplicates(subset = ['gene', 'variant'], inplace = True)
    keys = list(zip(tmp_df_final_res.gene, tmp_df_final_res.variant))
    df_variant_ACMG_interpret = pd.DataFrame()
    df_variant_ACMG_interpret_chinese = pd.DataFrame() 
    for key in keys:
        if key in curr_interpret.keys():
            interpret = ' '.join(curr_interpret[key])
            variant_ACMG_interpret[key].append(('Phenotype filter', interpret))
        if key in curr_interpret_chinese.keys():
            interpret_chinese = ' '.join(curr_interpret_chinese[key])
            variant_ACMG_interpret_chinese[key].append(('表型深度筛选', interpret_chinese))
        tmp_df = pd.DataFrame(variant_ACMG_interpret[key], columns = ['criteria', 'interpretation'])
        tmp_df['gene'] = key[0]
        tmp_df['variant'] = key[1]
        tmp_df = tmp_df[['gene', 'variant', 'criteria', 'interpretation']] 
        df_variant_ACMG_interpret = pd.concat([df_variant_ACMG_interpret, tmp_df])

        tmp_df = pd.DataFrame(variant_ACMG_interpret_chinese[key], columns = ['criteria', 'interpretation'])
        tmp_df['gene'] = key[0]
        tmp_df['variant'] = key[1]
        tmp_df = tmp_df[['gene', 'variant', 'criteria', 'interpretation']] 
        # tmp_df.columns = ['基因', '变异', '标准', '解读']                 
        df_variant_ACMG_interpret_chinese = pd.concat([df_variant_ACMG_interpret_chinese, tmp_df])
    
    return df_final_res, df_variant_ACMG_interpret, df_variant_ACMG_interpret_chinese