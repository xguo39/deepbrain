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
import os.path
BASE = os.path.dirname(os.path.abspath(__file__))

start_program = time.time()

reload(sys)
sys.setdefaultencoding("utf-8")

db = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="Tianqi12",
                     db="DB_offline")

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
    return updated_top_variants, updated_protein_domains, updated_variantsdata

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
    genes = [var[0] for var in protein_domains.keys()]
    genes = '(' +', '.join("'" + item + "'" for item in genes) + ')'
    query = "select d.gene, m.variant, m.protein, d.protein_domains from var2proteindomains d, genevariantproteinmapping m where d.gene in %s and d.gene = m.gene and (d.protein_variant = m.variant or d.protein_variant = m.protein)" % genes
    cursor = db.cursor()
    cursor.execute(query)
    dbdata = cursor.fetchall()

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
        values = samedomainvariants[key]
        for value in values:
            if value not in samedomainvariants.keys():
                domainvariants2original[value] = key
            else:
                domainvariants2original[value] = value
    return samedomainvariants, domainvariants2original 


def queryPhenosFromDB(samedomainvariants, domainvariants2original):
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
    return variantphenosfromDB

def initWordDifficultyIndex():
    global word_difficulty_index
    df = pd.read_csv(os.path.join(BASE, 'data/word_difficulty_index.txt'), usecols = [0, 1, 2])
    word_difficulty_index = df.set_index(['Word']).to_dict()['Freq_HAL']
    return word_difficulty_index

def searchPhenosFromPubmed(patient_phenotypes, samedomainvariants, domainvariants2original):
    global word_difficulty_index, patient_phenotypes_wordbreak
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

    # break terms to word list: 'pulmonary hypoplasia' -> ['pulmonary', 'hypoplasia']
    patient_phenotypes_wordbreak = []
    for pheno in patient_phenotypes:
        pheno_wordlist = pheno.split()
        #pheno_wordlist = [singularize(word, custom={'toes':'toe'}) for word in pheno_wordlist]
        append_wordlist = False 
        for word in pheno_wordlist:
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
    # print patient_phenotypes_wordbreak
    re_pubmed = re.compile(r'\b(' +'|'.join(patient_phenotypes_wordbreak) + r')', re.I)

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
                    else:
			variantphenosfromPubmed[originalvar] = re_pubmed.findall(text) 
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
        # print "Opposite meaning due to word 'poor'", words_in_pheno_only, words_in_hpo_only
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
                if words_in_patient_pheno_only and words_in_var_pheno_only and isOppositeMeaning(words_in_var_pheno_only, words_in_patient_pheno_only):
                    variants_with_opposite_phenos.append(var) 
    return list(set(variants_with_opposite_phenos))

def getScores(variantphenosfromPubmed, variantphenosfromDB, variantphenos, patient_phenotypes):
    global patient_phenotypes_wordbreak, word_difficulty_index
    scores = dict()
    variantphenosfromPubmedAndDB = dict()
    # convert pubmed matched text to lower case
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
    # print variantphenosfromPubmedAndDB

    for originalvar in variantphenosfromPubmed.keys():
	items_count = Counter(variantphenosfromPubmed[originalvar])
	#print items_count
	for item in items_count.keys():
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
        # print num_match_phenos, num_all_var_phenos, num_all_patient_phenos
        scores[originalvar] = 1.0 + np.sqrt(scores[originalvar]) * np.sqrt(num_match_phenos / num_all_var_phenos) * np.sqrt(num_match_phenos / num_all_patient_phenos)
    # print scores
   
    # Make sure the phenos associated with variants do not have conflicts with the patient's phenos
    global lemmatizer, processed_antonyms
    lemmatizer = WordNetLemmatizer()
    processed_antonyms = dict()
    variants_with_opposite_phenos = identifyVariantsWithOppositePhenos(variantphenos, patient_phenotypes)
    # print variants_with_opposite_phenos
    for originalvar in variants_with_opposite_phenos:
        if originalvar in scores:
            scores[originalvar] = scores[originalvar] * 0.9
        else:
            scores[originalvar] = 1.0 * 0.9
    # print scores
    return scores

def generateOutput(variants, ACMG_result, patient_phenotypes): 
    global patient_phenotypes_wordbreak
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
    df_final_res.sort(['final_score'], ascending = [0], inplace = True)
    return df_final_res

