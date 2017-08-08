# -*- coding: utf-8 -*-

import pandas as pd
import re
from nltk.corpus import wordnet as wn
from collections import deque
from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter
import os.path
import numpy as np
import MySQLdb
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

reload(sys)
sys.setdefaultencoding("utf-8")

"""
For each input phenotype of the patient, we do preliminary mapping of it to hpo standard terms.
We convert the input phenotype term and hpo standard terms to a word list and strip symbols in the word and lemmatize the word.
The word list of hpo standard term and its synonyms and the word list of input phenotype are compared and if they are a match or partial match and they do not contain non-overlapped words with opposite meanings, we consider the hpo term as a candidate.
The matched hpo terms are filtered on their common ancestors, which basically reflect semantics of the hpo terms. The hpo term with the highest similarity score is used as the gold standard. If another hpo candidate has a very high level common ancestor (not close in semantics) with it, then that hpo candidate will be removed. Matches after this filtering step are direct matches (from input phenotype).
We also get indirect matches by mapping the synonyms of hpo term with very high similarity score to other hpo terms. 
The direct and indirect matches are combined and if they do not have non-overlapped opposite meaning words, they are taken into the final matches.

The hpo dictionary is like a graph. It has a root node.
hpo_subclass: dictionary with a hpo term (id) as key and its direct children as value.
hpo_superclass: dictionary with a hpo term (id) as key and its direct parents as value.
"""

HPO_SUBCLASS = os.path.join(BASE, "data/hpo_subclasses.txt")
HPO_SUPERCLASSES = os.path.join(BASE, "data/hpo_superclasses.txt")
HPO_NAMES = os.path.join(BASE, "data/hpo_names.txt")
HPO_FILE = os.path.join(BASE, "data/all_hpo_terms_and_synonyms.txt")
PHENOTYPE_TO_GENE_FILE = os.path.join(BASE, "data/Expanded_OMIM_ALL_FREQUENCIES_phenotype_to_genes_without_synonym.txt")
PHENOTYPE_TO_DISEASE_FILE = os.path.join(BASE, 'data/Expanded_ALL_SOURCES_ALL_FREQUENCIES_diseases_to_phenotypes.txt')

## Get levels of each hpo term; e.g., HP:0000001 is the first level; its direct children are the second level.
## Phenotypic abnormality is level 1; Abnormality of prenatal development or birth is level 2.
## In the search for the common ancestors, we should stop at level 2; if two terms have the common ancestor below or equal at level 2, then we deem them to be semantically similar.

PHENOTYPE_COUNT_FILE = os.path.join(BASE, 'data/hpoid_count_in_pubmed.txt')
df_pheno_count = pd.read_csv(PHENOTYPE_COUNT_FILE, sep = '\t', usecols = [0, 2])
hpoidpheno_count = df_pheno_count.set_index('hpoid')['count'].to_dict()

hpo_subclass = dict()
with open(HPO_SUBCLASS, 'rb') as f:
    # skip the first header line
    f.readline()
    for line in f.readlines():
        line = line.rstrip()
        parts = line.split('\t')
        hpoid = parts[0]
        subclasses = parts[1].strip('[]').replace("'", "")
        subclasses = [_.strip() for _ in subclasses.split(',')]
        hpo_subclass[hpoid] = subclasses

hpo_levels = dict()
level = 0
root = 'HP:0000001'
curr_level_nodes = [root] 
while curr_level_nodes:
    next_level_nodes = []
    for node in curr_level_nodes:
        hpo_levels[node] = level
        if node in hpo_subclass:
            next_level_nodes += hpo_subclass[node]
    curr_level_nodes = next_level_nodes
    level += 1
     

hpo_superclass = dict()
with open(HPO_SUPERCLASSES, 'rb') as f:
    # skip the first header line
    f.readline()
    for line in f.readlines():
        line = line.rstrip()
        parts = line.split('\t')
        hpoid = parts[0]
        superclasses = parts[1].strip('[]').replace("'", "")
        superclasses = [_.strip() for _ in superclasses.split(',')]
        hpo_superclass[hpoid] = superclasses

hpo_name = dict()
with open(HPO_NAMES, 'rb') as f:
    # Skip the first header line
    f.readline()
    for line in f.readlines():
        line = line.rstrip()
        parts = line.split('\t')
        hpoid = parts[0]
        hponame = parts[1]
        hpo_name[hpoid] = hponame        

# tree = hpo_superclass
def getAllAncestorsBFS(node, tree):

    """ get all ancestors of a node using BFS

    Args:
        node (string): node in a tree
        tree (dict): dictionary with node as key and its direct parents as value

    Returns:
        P (list): the ancestors of a node with the first element as the direct parent and so on

    """

    P, Q = [node], deque([node])
    while Q:
        u = Q.popleft()
        if u not in tree:
            continue
        for v in tree[u]:
            if v in P: continue
            if v not in tree: continue
            P.append(v)
            Q.append(v)
    # Append All ('HP:0000001') as the highest ancestor 
    P.append('HP:0000001')
    return P 

def findLowestCommonAncestor(node1, node2, tree):

    """ find the lowest common ancestor of two nodes in a tree

    Args:
        node1 (string): hpoid of a phenotype
        node2 (string): hpoid of another phenotype
        tree (dict): dictionary with key as a node and value as the direct parents of the node

    Returns:
        lca (tuple): lowest common ancestor (hpoid, level, hponame)
        common_ancestors (list): common ancestors from lowest common ancestor to top level common ancestor

    """

    node1_ancestors = getAllAncestorsBFS(node1, tree) 
    node2_ancestors = getAllAncestorsBFS(node2, tree)
    common_ancestors = [] 
    for ancestor in node2_ancestors:
        if ancestor in node1_ancestors:
            name = hpo_name[ancestor]
            level = hpo_levels[ancestor]
            common_ancestors.append((ancestor, level, name)) 
    lca = common_ancestors[0]
    return lca, common_ancestors

## Generate antonyms of a word using NLTK and wordnet
def get_antonyms(word):

    """ generate antonyms of a word using NLTK and wordnet

    Args:
        word (string): input word

    Returns:
         antonyms (set): a set of antonyms of the input word

    """

    antonyms = []
    for synset in wn.synsets(word):
        for lemma in synset.lemmas():
            antonyms += lemma.antonyms()
            similar_synsets = synset.similar_tos() 
            for similar_synset in similar_synsets:
                for lemma_ in similar_synset.lemmas():
                    #print (similar_synset, lemma_, lemma_.name(), 
                    #      lemma_.antonyms(), similar_synset.similar_tos())
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


with open(HPO_FILE, 'rb') as infile:
    hpo_name2id = dict()
    hpo_id2synonyms = dict()
    # skip the first line
    infile.readline()
    for line in infile.readlines():
        line = line.rstrip()
        parts = line.split('\t')
        hpoid, hponame = parts[0], parts[1]
        hpo_name2id[hponame] = hpoid
        hpoid = hpoid.split('-')[0]
        if hponame in hpo_id2synonyms:
            hpo_id2synonyms[hpoid].append(hponame)
        else:
            hpo_id2synonyms[hpoid] = [hponame]
    hpo_terms = hpo_name2id.keys()  


# Use re for split hpo terms
# Use lemmatizer to lemmatize words e.g., disturbances --> distrubance
processed_antonyms = dict()
def isOppositeMeaning(words_in_pheno_only, words_in_hpo_only):
    """ check if the input two word lists contain words with opposite meaning

    Args:
        words_in_pheno_only (set): a set of words that appear in the phenotype word list only
        word_in_hpo_only (set): a set of words that appear in the hpo term word list only

    Returns:
         bool: True or False

    """

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
            # antonyms = get_antonyms(word)
            if word in processed_antonyms:
                antonyms = processed_antonyms[word]
            else:
                #print "get antonyms for word:", word
                antonyms = get_antonyms(word)
                processed_antonyms[word] = antonyms
        except UnicodeDecodeError as e:
            continue
        if antonyms.intersection(words_in_hpo_only):
            # print "Opposite meaning: ", antonyms.intersection(words_in_hpo_only)
            return True  
    for word in words_in_hpo_only:
        try:
            # antonyms = get_antonyms(word)
            if word in processed_antonyms:
                antonyms = processed_antonyms[word]
            else:
                #print "get antonyms for word:", word
                antonyms = get_antonyms(word)
                processed_antonyms[word] = antonyms

        except UnicodeDecodeError as e:
            continue
        if antonyms.intersection(words_in_pheno_only):
            # print "Opposite meaning: ", antonyms.intersection(words_in_hpo_only)
            return True  
    return False 

def processhpoterms(hpo_):
    """ process each hpo term by transforming each term to a list of individual words, and strip ,()' in the word
        and lemmatize each word. Use a global dictionary to record the mapping from original hpo term to the processed list.
        Use re for split hpo terms
        Use lemmatizer to lemmatize words e.g., disturbances --> distrubance

    Args:
        hpo_ (string); a hpo term

    Returns:
        None

    """

    global hpo_words_dict
    hpo_words =  [_.strip(",()'") for _ in re.split(' |/', hpo_)]
    try:
        hpo_words = [lemmatizer.lemmatize(word) for word in hpo_words]
    except UnicodeDecodeError as e:
        pass
    hpo_words_dict[hpo_] = hpo_words

# If the opposite meanings are found for a hpoid, then its synonyms are all in opposite meanings
unmatches_due_to_opposite_meanings = []
hpo_words_dict = dict()
# Use lemmatizer to lemmatize words e.g., disturbances --> distrubance
lemmatizer = WordNetLemmatizer()

def map2hpo(pheno):
    """ preliminary mapping of each input phenotype of the patient to hpo standard terms

    Args:
        pheno (string): an input phenotype of the patient

    Returns:
        matches (list): each element is a tuple (hpoid, hponame, match_type, similarity_score)
            e.g., [('HP:0012171', 'Stereotypical hand wringing', 'OVERLAP', 0.6666666666666666), ...]
    """

    global unmatches_due_to_opposite_meanings, hpo_words_dict
    matches = []
    # Use lemmatizer to lemmatize words e.g., disturbances --> distrubance
    # lemmatizer = WordNetLemmatizer()
    pheno_ = pheno.lower() 
    pheno_words = [_.strip(",()'") for _ in re.split(' |/', pheno_)]
    try:
        pheno_words = [lemmatizer.lemmatize(word) for word in pheno_words]
    except UnicodeDecodeError as e:
        pass   


    for hpo in hpo_terms:
        hpoid = hpo_name2id[hpo]
        # pheno_ = pheno.lower()
        hpo_ = hpo.lower()
        if hpo_.startswith('obsolete '):
            continue 
        if pheno_ == hpo_:
            matches.append((hpoid, hpo, 'EXACT', 1.0)) 
            continue
        # pheno_words = [_.strip(",()'") for _ in re.split(' |/', pheno_)]
        # hpo_words = [_.strip(",()'") for _ in re.split(' |/', hpo_)]
        if hpo_ not in hpo_words_dict:
            processhpoterms(hpo_)
        hpo_words = hpo_words_dict[hpo_]

        '''
        # This is a corner case. Developmental delay means retarded and growth delay means short. 
        # But in plain language, they are exchangable.
        for pheno_word in pheno_words:
            if re.search('development', pheno_word, re.I):
                pheno_words.append('growth') 
            if re.search('growth', pheno_word, re.I):
                pheno_words.append('developmental') 
        '''
        # try:
        #     pheno_words = [lemmatizer.lemmatize(word) for word in pheno_words]
        #     hpo_words = [lemmatizer.lemmatize(word) for word in hpo_words]
        # except UnicodeDecodeError as e:
        #     pass
        if pheno_words == hpo_words:
            matches.append((hpoid, hpo, 'LEMMA_MATCH', 1.0)) 
            continue
        if set(pheno_words) == set(hpo_words):
            matches.append((hpoid, hpo, 'REORDER', 1.0)) 
            continue

        common_words = set(pheno_words) & set(hpo_words)
        if not common_words:
            continue

        words_in_pheno_only = set(pheno_words) - common_words
        words_in_hpo_only = set(hpo_words) - common_words
        # check if the pheno and hpo are in opposite meaning
        # if any word in pheno is an antonym of a word in hpo, or the other way
        # we skip this hpo
        sim = float(len(common_words)) / max(len(hpo_words), len(pheno_words))  
        if (sim >= 0.3333) and (pheno_ in hpo_) and (len(hpo_words) <= 10 * len(pheno_words)):
            if not isOppositeMeaning(words_in_pheno_only, words_in_hpo_only):
                matches.append((hpoid, hpo, 'SUB', sim))
            else:
                unmatches_due_to_opposite_meanings.append(hpoid.split('-')[0])
            continue
        if (sim >= 0.3333) and (hpo_ in pheno_) and (len(pheno_words) <= 10 * len(hpo_words)): 
            if not isOppositeMeaning(words_in_pheno_only, words_in_hpo_only):
                matches.append((hpoid, hpo, 'SUPER', sim))
            else:
                unmatches_due_to_opposite_meanings.append(hpoid.split('-')[0])
            continue
        if (sim >= 0.5) and len(pheno_words) >= 2:
            if not isOppositeMeaning(words_in_pheno_only, words_in_hpo_only):
                matches.append((hpoid, hpo, 'OVERLAP', sim))
            else:
                unmatches_due_to_opposite_meanings.append(hpoid.split('-')[0])
    matches_res = []
    for match in matches:
        if match[0].split('-')[0] not in unmatches_due_to_opposite_meanings:
            matches_res.append(match)
    matches = matches_res
    return matches

def filterMatchesOnCommonAncestors(matches):
    """ this function filters matches on common ancestors. One input phenotype may map to multiple hpo standard terms
        with different similarity score. We pick up the one with best match score, and check the common ancestor of
        other hpo terms with it. The common ancestor is literally in the cengji jigou, e.g., abnormality of head -- abnormality
        of eye -- baineichang. If the common ancestor of a hpo term and the best-match hpo term are very high level, then they are likely NOT
        describing the same phenotype. This hpo term will be removed from the matches.

    Args:
        matches (list): each element is a tuple (hpoid, hponame, match_type, similarity_score)
            e.g., [('HP:0012171', 'Stereotypical hand wringing', 'OVERLAP', 0.6666666666666666), ...]

    Returns:
        final_matches (list): each element is a tuple (hponame, hpoid, similarity_score).
            e.g., [('Postnatal macrocephaly','HP:0005490',0.5), ('Macrocephaly,relative','HP:0004482-synonym', 0.5), ...]

    """

    if not matches:
        return matches 
    final_matches = []
    # If the match is a disease not a phenotype, then we just add it to the final matches result
    matches_tmp = []
    for match in matches:
        if not match[0].startswith('HP:'):
            final_matches.append((match[1], match[0], match[3]))
        else:
            matches_tmp.append(match)
    matches = matches_tmp
    if not matches:
        return final_matches
    best_match_hpo = sorted(matches, key = lambda x: x[3], reverse = True)[0][0]
    for match in matches:
        term = match[0]
        # Remove 'synonym' from the hpoid (term) e.g., HP:0004414-synonym --> HP:0004414
        term = term.split('-')[0]
        lca, common_ancestors = findLowestCommonAncestor(term, best_match_hpo.split('-')[0], hpo_superclass)
        if lca[1] >= 2:
            final_matches.append((match[1], match[0], match[3])) 
    return final_matches    

def map2hpoWithPhenoSynonyms(pheno):
    """ map each input phenotype of the patient to hpo standard terms

    Args:
        pheno (string): an input phenotype of the patient 

    Returns: 
        final_matches (list): each element is a tuple (hponame, hpoid, similarity_score)
            e.g., [('Postnatal macrocephaly','HP:0005490',0.5), ('Macrocephaly,relative','HP:0004482-synonym', 0.5), ...]

    """

    global unmatches_due_to_opposite_meanings
    matches = map2hpo(pheno)
    direct_matches = filterMatchesOnCommonAncestors(matches)  
    final_matches = direct_matches 
    for match in direct_matches:
        hponame = match[0]
        hpoid = match[1].split('-')[0]
        sim = match[2]
        if sim >= 0.75:
            hposynonyms = hpo_id2synonyms[hpoid]
            for synonym in hposynonyms:
                if synonym != hponame:
                    matches_ = map2hpo(synonym)
                    indirect_matches = filterMatchesOnCommonAncestors(matches_)
                    final_matches = final_matches + indirect_matches
    final_matches = list(set(final_matches))
    matches_res = []
    for match in final_matches:
        if match[0].split('-')[0] not in unmatches_due_to_opposite_meanings:
            matches_res.append(match)
    final_matches = matches_res
    unmatches_due_to_opposite_meanings = []
    return final_matches

hpoid2gene = dict()
with open(PHENOTYPE_TO_GENE_FILE, 'rb') as f:
    # skip the first header line
    f.readline()
    for line in f.readlines():
        line = line.rstrip()
        parts = line.split('\t')
        geneid, genesymbol, hponame, hpoid = parts[0], parts[1], parts[2], parts[3]
        if hpoid in hpoid2gene:
            hpoid2gene[hpoid].append(genesymbol)   
        else:
            hpoid2gene[hpoid] = [genesymbol]

def map2gene(final_matches, CANDIDATE_GENES):
    """ Map to genes for each phenotype without similarity score (one phenotype at one time)

    Args:
        final_matches (list): each element is a tuple (hponame, hpoid, similarity_score)
        CANDIDATE_GENES (list): input candidate genes of the patient
       
    Returns:
        mapped_genes (list): genes associated with the phenotype 

    """

    # Map to genes for each phenotype (one phenotype at one time)
    # Pre-process the final_matches by remove '-synonym' from the hpoid and then unique the hpoids
    final_matches = [_[1] for _ in final_matches] 
    final_matches = [_.split('-')[0] for _ in final_matches] 
    final_matches = list(set(final_matches))
    mapped_genes = []
    for hpoid in final_matches:
        try:
            mapped_genes += hpoid2gene[hpoid] 
        except KeyError:
            pass
    ## For each phenotype in patient record, we generated multiple phenotype keywords 
    ## to maximize the mapping to the genes. However, we only count it once for each 
    ## phenotype even if the multiple keywords lead to multiple mappings.
    ## In practice, we don't need to screen through all genes. Only a few gene candidates are examined.
    mapped_genes = list(set(mapped_genes) & set(CANDIDATE_GENES))
    return mapped_genes, final_matches

def map2geneWithSim(final_matches, CANDIDATE_GENES, associated_genes_for_curr_pheno_from_pubmed):
    """ Map to genes for each phenotype (one phenotype at one time) with similarity score 
    final_matches like: [('Postnatal macrocephaly','HP:0005490',0.5), ('Macrocephaly,relative','HP:0004482-synonym', 0.5), ...]

    Args:
        final_matches (list): each element is a tuple (hponame, hpoid, similarity_score)
        CANDIDATE_GENES (list): input candidate genes of the patient
        associated_genes_for_curr_pheno_from_pubmed (list): genes associated with patient's phenotypes searched form Pubmed

    Returns:
        mapped_genes_score (dict): a dict with gene symbol as key and similarity score as value 
        mapped_genes_score_phenospecificity (dict): a dict with gene symbol as key and similarity score 
            that is weighted by phenotype rareness as value 

    """

    global hpoidpheno_count
    hpoid_sim = dict() 
    for match in final_matches:
        hpoid = match[1].split('-')[0]
        sim = match[2]
        if hpoid not in hpoid_sim or sim > hpoid_sim[hpoid]:
            hpoid_sim[hpoid] = sim
    mapped_genes_score = dict()
    ##**** new
    mapped_genes_score_phenospecificity = dict()

    for hpoid in hpoid_sim:
        try:
            mapped_genes = hpoid2gene[hpoid]
            # add genes searched from pubmed
            mapped_genes = list(set(mapped_genes + associated_genes_for_curr_pheno_from_pubmed))
        except KeyError:
            if not associated_genes_for_curr_pheno_from_pubmed:
                continue
            else:
                mapped_genes = associated_genes_for_curr_pheno_from_pubmed
        sim = hpoid_sim[hpoid]
        for gene in mapped_genes:
            # In practice, we don't need to screen through all genes. 
            # Only a few gene candidates are examined.
            if gene not in CANDIDATE_GENES:
                continue
            if gene not in mapped_genes_score or sim > mapped_genes_score[gene]:
                mapped_genes_score[gene] = sim
                ##**** new
                if hpoid in hpoidpheno_count:
                    pheno_weight = 6.0 / np.log(hpoidpheno_count[hpoid] + 2.7183) 
                else: 
                    pheno_weight = 6.0  
                mapped_genes_score_phenospecificity[gene] = sim * pheno_weight
    ##**** new
    return mapped_genes_score, mapped_genes_score_phenospecificity 

hpoid2disease = dict()
numphenosindisease = dict()
with open(PHENOTYPE_TO_DISEASE_FILE, 'rb') as f:
    # skip the first header line
    f.readline()
    for line in f.readlines():
        line = line.rstrip()
        parts = line.split('\t')
        diseaseid, hpoid, hponame, diseasename = parts[0], parts[1], parts[2], parts[3]
        if diseasename in numphenosindisease:
            numphenosindisease[diseasename] += 1
        else:
            numphenosindisease[diseasename] = 1
        if hpoid in hpoid2disease:
            hpoid2disease[hpoid].append(diseasename)
        else:
            hpoid2disease[hpoid] = [diseasename]

def map2disease(final_matches):
    """ Map to diseases for each phenotype without similarity score (one phenotype at one time)

    Args:
        final_matches (list): each element is a tuple (hponame, hpoid, similarity_score)
       
    Returns:
        mapped_diseases (list): diseases associated with the phenotype 

    """
    # Map to diseases for each phenotype (one phenotype at one time)
    # Pre-process the final_matches by remove '-synonym' from the hpoid and then unique the hpoids
    final_matches = [_[1] for _ in final_matches] 
    final_matches = [_.split('-')[0] for _ in final_matches] 
    final_matches = list(set(final_matches))
    mapped_diseases = []
    for hpoid in final_matches:
        try:
            mapped_diseases += hpoid2disease[hpoid] 
        except KeyError:
            pass
    ## For each phenotype in patient record, we generated multiple phenotype keywords 
    ## to maximize the mapping to the genes. However, we only count it once for each 
    ## phenotype even if the multiple keywords lead to multiple mappings.
    ## In practice, we don't need to screen through all genes. Only a few gene candidates are examined.
    #mapped_genes = list(set(mapped_genes) & set(CANDIDATE_GENES))
    return mapped_diseases

def map2diseaseWithSim(final_matches):
    """ Map to diseases for each phenotype (one phenotype at one time) with similarity score 
    final_matches like: [('Postnatal macrocephaly','HP:0005490',0.5), ('Macrocephaly,relative','HP:0004482-synonym', 0.5), ...]

    Args:
        final_matches (list): each element is a tuple (hponame, hpoid, similarity_score)

    Returns:
        mapped_diseases_score (dict): a dict with diseasename as key and similarity score as value 

    """
    hpoid_sim = dict() 
    for match in final_matches:
        hpoid = match[1].split('-')[0]
        sim = match[2]
        if hpoid not in hpoid_sim or sim > hpoid_sim[hpoid]:
            hpoid_sim[hpoid] = sim
    mapped_diseases_score = dict()
    for hpoid in hpoid_sim:
        try:
            mapped_diseases = hpoid2disease[hpoid]
        except KeyError:
            continue
        sim = hpoid_sim[hpoid]
        for disease in mapped_diseases:
            # In practice, we don't need to screen through all genes. 
            # Only a few gene candidates are examined.
            #if disease not in CANDIDATE_DISEASES:
            #    continue
            if disease not in mapped_diseases_score or sim > mapped_diseases_score[disease]:
                mapped_diseases_score[disease] = sim
    return mapped_diseases_score 

def getRelatedPubmedArticles(phenos, CANDIDATE_GENES):
    db = MySQLdb.connect(host="localhost",
                 user="root",
                 passwd="Tianqi12",
                 db="DB_offline")

    variantphenosfromPubmed = dict()
    query = "select gene, protein_variant, pmid, title, abstract from pubmed_var where "
    for gene in CANDIDATE_GENES:
        query += "gene = '%s' or " % gene
    query = query[0:-4]
    cursor = db.cursor()
    cursor.execute(query)
    pubmed_data = cursor.fetchall()
    db.close()
    return pubmed_data

def initWordDifficultyIndex():
    df = pd.read_csv(os.path.join(BASE, 'data/word_difficulty_index.txt'), usecols = [0, 1, 2])
    df['Word'] = df['Word'].str.lower()
    word_difficulty_index = df.set_index(['Word']).to_dict()['Freq_HAL']
    return word_difficulty_index

def searchPhenosFromPubmed(phenos, CANDIDATE_GENES):
    pubmed_data = getRelatedPubmedArticles(phenos, CANDIDATE_GENES)
    word_difficulty_index = initWordDifficultyIndex()
    patient_phenotypes_wordbreak = []
    phenowordbreak2originalpheno = dict()
    for pheno in phenos:
        pheno_wordlist = pheno.split()
        append_wordlist = False
        for word in pheno_wordlist: 
            word = word.lower()
            if word not in word_difficulty_index.keys() or word_difficulty_index[word] < 100:
                append_wordlist = True
                rare_words_in_pheno_wordlist = [word for word in pheno_wordlist if word not in word_difficulty_index or word_difficulty_index[word] < 1000]
                patient_phenotypes_wordbreak += rare_words_in_pheno_wordlist
                for rare_word in rare_words_in_pheno_wordlist:
                    phenowordbreak2originalpheno[rare_word.lower()] = pheno
                break
        if not append_wordlist:
            patient_phenotypes_wordbreak.append(pheno)
            phenowordbreak2originalpheno[pheno.lower()] = pheno

    tmp_patient_phenotypes_wordbreak = []
    for pheno in patient_phenotypes_wordbreak:
        if pheno not in word_difficulty_index.keys() or word_difficulty_index[pheno] < 160000:
            tmp_patient_phenotypes_wordbreak.append(pheno)
    patient_phenotypes_wordbreak = tmp_patient_phenotypes_wordbreak

    re_pubmed = re.compile(r'\b(' +'|'.join(patient_phenotypes_wordbreak) + r')', re.I)

    phenosgenefromPubmed = dict()
    genephenosfromPubmed = dict()
    genephenospmids = dict()
    for data in pubmed_data:
        gene, protein_variant, pmid, title, abstract = data
        text = title + ' ' + abstract
        if not re_pubmed.search(text):
            continue
        pubmed_phenos_wordbreak = re_pubmed.findall(text)
        if gene in genephenosfromPubmed:
            genephenosfromPubmed[gene] += [phenowordbreak2originalpheno[pheno.lower()] for pheno in pubmed_phenos_wordbreak]
            genephenospmids[gene].append(pmid)
        else:
            genephenosfromPubmed[gene] = [phenowordbreak2originalpheno[pheno.lower()] for pheno in pubmed_phenos_wordbreak]
            genephenospmids[gene] = [pmid]
        for pheno_wordbreak in pubmed_phenos_wordbreak:
            pheno = phenowordbreak2originalpheno[pheno_wordbreak.lower()] 
            if pheno in phenosgenefromPubmed:
                phenosgenefromPubmed[pheno].append(gene)
            else:
                phenosgenefromPubmed[pheno] = [gene]

    # make the value in each dict to be a unique list 
    for key in phenosgenefromPubmed.keys():
        phenosgenefromPubmed[key] = list(set(phenosgenefromPubmed[key]))
    for key in genephenosfromPubmed.keys():
        genephenosfromPubmed[key] = list(set(genephenosfromPubmed[key]))
    for key in genephenospmids.keys():
        genephenospmids[key] = list(set(genephenospmids[key]))

    return phenosgenefromPubmed

def generate_score(phenos, CANDIDATE_GENES, corner_cases, original_phenos):
    """ This is the main function in this .py file. It is called in the main.py file.

    Args:
        phenos (list): input patient's phenotypes
        CANDIDATE_GENES (list): input candidate genes of the patient
        corner_cases (dict): corner cases of input patient's phenotypes that need to be handled. Currently the corner cases are to make growth delay and development delay interchangebly. 
        original_phenos (list): input patient's phenotypes before handling the corner cases

    Returns:
        ranking_genes (list): each element in the list is a tuple (gene, score, hits, phenospecificity_score). 
            It records gene symbol, phenotype hit score for this gene, nubmer of phenotypes associated with this gene, 
            and the phenotype correlation score by weighing the rareness of each phenotype.  
        ranking_diseases (list): each element in the list is a tuple (disease, score, hits). 
            It records the disease name, phenotype hit score for this disease, and number of phenotypes associated with this disease.
        gene_associated_phenos (dict): phenotypes associated with each gene

    """
    all_mapped_genes = []
    all_mapped_genes_score = {}
    gene_phenos = {} 
    all_mapped_diseases = []
    all_mapped_diseases_score = {}
    disease_phenos = {} 

    gene_associated_phenos = dict()
    all_mapped_genes_score_phenospecificity = {}
    gene_associated_pheno_hpoids = dict()

    # Get phenotype-gene associations from Pubmed
    phenosgenefromPubmed = searchPhenosFromPubmed(phenos, CANDIDATE_GENES)

    for pheno in phenos:
        # print ("===========================================================================================")
        # pprint.pprint(pheno)
        # matches =  map2hpo(pheno)
        final_matches = map2hpoWithPhenoSynonyms(pheno)
        # pprint.pprint(final_matches)
        mapped_genes, final_matches_hpoids = map2gene(final_matches, CANDIDATE_GENES)

        for gene in mapped_genes:
            if pheno not in original_phenos:
                continue
            if gene in gene_associated_phenos:
                gene_associated_phenos[gene].append(pheno)
            else:
                gene_associated_phenos[gene] = [pheno]
            if gene in gene_associated_pheno_hpoids:
                gene_associated_pheno_hpoids[gene] += final_matches_hpoids
            else:
                gene_associated_pheno_hpoids[gene] = final_matches_hpoids

        # Add genes searched from pubmed to gene_associated_phenos
        associated_genes_for_curr_pheno_from_pubmed = []
        if pheno in phenosgenefromPubmed:   
            associated_genes_for_curr_pheno_from_pubmed = phenosgenefromPubmed[pheno] 
        for gene in associated_genes_for_curr_pheno_from_pubmed:
            if gene in mapped_genes:
                continue
            if gene in gene_associated_phenos:
                gene_associated_phenos[gene].append(pheno)
            else:
                gene_associated_phenos[gene] = [pheno]
            if gene in gene_associated_pheno_hpoids:
                gene_associated_pheno_hpoids[gene] += final_matches_hpoids
            else:
                gene_associated_pheno_hpoids[gene] = final_matches_hpoids

        # pprint.pprint(mapped_genes)
        all_mapped_genes += list(set(mapped_genes) | set(associated_genes_for_curr_pheno_from_pubmed))
        mapped_genes_score, mapped_genes_score_phenospecificity = map2geneWithSim(final_matches, CANDIDATE_GENES, associated_genes_for_curr_pheno_from_pubmed)
        if pheno in corner_cases:
            pheno = corner_cases[pheno]
        for gene in mapped_genes_score:
            if gene not in all_mapped_genes_score:
                all_mapped_genes_score[gene] = mapped_genes_score[gene]
                all_mapped_genes_score_phenospecificity[gene] = mapped_genes_score_phenospecificity[gene]
            else:
                all_mapped_genes_score[gene] += mapped_genes_score[gene]
                all_mapped_genes_score_phenospecificity[gene] += mapped_genes_score_phenospecificity[gene]
            if gene not in gene_phenos:
                gene_phenos[gene] = [pheno]
            else:
                gene_phenos[gene].append(pheno)

        mapped_diseases = map2disease(final_matches)
        # pprint.pprint(mapped_diseases)
        all_mapped_diseases += mapped_diseases
        mapped_diseases_score = map2diseaseWithSim(final_matches)
        for disease in mapped_diseases_score:
            if disease not in all_mapped_diseases_score:
                all_mapped_diseases_score[disease] = mapped_diseases_score[disease]
            else:
                all_mapped_diseases_score[disease] += mapped_diseases_score[disease]
            if disease not in disease_phenos:
                disease_phenos[disease] = [pheno]
            else:
                disease_phenos[disease].append(pheno)

    # make gene associated pheno hpoids unique
    for gene in gene_associated_pheno_hpoids.keys():
        value = list(set(gene_associated_pheno_hpoids[gene]))
        gene_associated_pheno_hpoids[gene] = value 

    num_patient_phenos = len(phenos)
    for disease in all_mapped_diseases_score:
        numphenos = numphenosindisease[disease]
        disease_score = all_mapped_diseases_score[disease]
        # print disease, numphenos, num_patient_phenos, disease_score
        # algo to calculate the disease score
        all_mapped_diseases_score[disease] = disease_score ** 2 / float(numphenos) / (1 + num_patient_phenos - disease_score)

    all_mapped_genes_score = [(k,v) for k, v in all_mapped_genes_score.items()]   
    all_mapped_genes_score = sorted(all_mapped_genes_score, key = lambda pair: pair[1], reverse = True)
    all_mapped_diseases_score = [(k,v) for k, v in all_mapped_diseases_score.items()]   
    all_mapped_diseases_score = sorted(all_mapped_diseases_score, key = lambda pair: pair[1], reverse = True)

    count = Counter(all_mapped_genes)
    count = sorted(count.items(), key = lambda pair: pair[1], reverse = True)
    count_disease = Counter(all_mapped_diseases)
    count_disease = sorted(count_disease.items(), key = lambda pair: pair[1], reverse = True)
    ranking_genes = []
    ranking_diseases = []
    for id in xrange(len(all_mapped_genes_score)):
        gene, score = all_mapped_genes_score[id]
        hits = None
        phenospecificity_score = all_mapped_genes_score_phenospecificity[gene]
        for gene_hits in count:
            if gene_hits[0] == gene:
                hits = gene_hits[1] 
                break
        if hits:
            ranking_genes.append((gene, score, hits, phenospecificity_score))

    for id in xrange(len(all_mapped_diseases_score)):
        disease, score = all_mapped_diseases_score[id]
        hits = None
        for disease_hits in count_disease:
            if disease_hits[0] == disease:
                hits = disease_hits[1] 
                break
        if hits:
            ranking_diseases.append((disease, score, hits))

    return ranking_genes, ranking_diseases, gene_associated_phenos, gene_associated_pheno_hpoids
