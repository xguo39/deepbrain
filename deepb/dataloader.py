import pandas as pd
import re
import numpy as np
from nltk.tokenize import sent_tokenize
from gensim.summarization import summarize
import amino_acid_mapping 
import sys
import pprint
import random
import copy

reload(sys)
sys.setdefaultencoding("utf-8")

'''
max number of sentences extracted from each abstract is: 5
max sentence length (cutoff threshold) is: 100
min sentence length (throw off threshold) is: 5
remove () and everything inside: True
keep '.', such as p.Asn308Ser: True
'''

def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9(),!?\'\%=`\.><\-_]", " ", string)
    string = re.sub(r"'s", " 's", string)
    string = re.sub(r"'ve", " 've", string)
    string = re.sub(r"n't", " n't", string)
    string = re.sub(r"'re", " 're", string)
    string = re.sub(r"'d", " 'd", string)
    string = re.sub(r"'ll", " 'll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " ( ", string)
    string = re.sub(r"\)", " ) ", string)
    string = re.sub(r"\?", " ? ", string)
    string = re.sub(r"'", " ' ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()
    #return string.strip()

def keywordSearch(keywords, text):
    if re.search(r'\b(' + '|'.join([re.escape(word) for word in keywords]) + r')\b', text, re.I):
        return True
    else:
        return False

def convertProtein1to3(protein):
    if not protein:
        return protein
    try:
        first = amino_acid_mapping.map1to3[protein[0]] 
    except KeyError:
        first = protein[0]
    try:
        last = amino_acid_mapping.map1to3[protein[-1]] 
    except KeyError:
        last = protein[-1]
    try:
        middle = protein[1:-1]
    except IndexError:
        return protein
    return first + middle + last

def getProteinSynonyms(protein):
    if not protein:
        return protein
    protein_synonyms = [protein]
    if re.match(r'[A-Z][0-9]', protein):
        protein_map = amino_acid_mapping.map1to3
        robj = re.compile('|'.join(protein_map.keys()))
        protein_syn = robj.sub(lambda m: protein_map[m.group(0)], protein)
    else:
        protein_map = amino_acid_mapping.map3to1
        robj = re.compile('|'.join(protein_map.keys()))
        protein_syn = robj.sub(lambda m: protein_map[m.group(0)], protein)
    protein_synonyms.append(protein_syn)
    return protein_synonyms

def filterSelectedSentences(keysents, keywords_genes, keywords_diseases):
    maxkeysents = 5 
    self_defined_keywords = ['associat', 'correla', 'caus', 'result', 'conclu', 'relat', 'lead', 'led', 'effect', 'make', 'made', 'bring', 'generat', 'prevent', 'creat', 'induc', 'produc', 'spawn', 'yield', 'inhibit', 'reason', 'reveal', 'indicat', 'confirm', 'disease', 'syndrome', 'risk']
    short_sents_removed, res = [], []
    for sent in keysents:
        if len(sent.split(' ')) < 5:
            continue
        if len(sent.split(' ')) >= 180:
            sent = ' '.join(sent.split(' ')[0:180])
        short_sents_removed.append(sent)
    if len(set(short_sents_removed)) <= maxkeysents:
        return list(set(short_sents_removed))
    res.append(short_sents_removed[-1])
    res.append(short_sents_removed[-2])
    res.append(short_sents_removed[-3])
    for sent in short_sents_removed:
        if (re.search(r'\b(' + '|'.join([re.escape(word) for word in keywords_genes]) + r')\b', sent, re.I) and
           re.search(r'\b(' + '|'.join([re.escape(word) for word in keywords_diseases]) + r')\b', sent, re.I)):
            res.append(sent)
    if len(set(res)) >= maxkeysents:
        res = list(set(res))
        return res[0:maxkeysents]
    for sent in short_sents_removed:
        if re.search('|'.join([re.escape(word) for word in self_defined_keywords]), sent, re.I):
            res.append(sent) 
    if len(set(res)) >= maxkeysents:
        res = list(set(res))
        return res[0:maxkeysents]
    sents_not_in_res = list(set(short_sents_removed) - set(res))
    num_sents_to_add = maxkeysents - len(res)
    lis = range(0, len(sents_not_in_res))
    random.shuffle(lis)
    for i in xrange(num_sents_to_add):
        res.append(sents_not_in_res[lis[i]])
    return list(set(res))

def summarize2OneSent(text):
    num_sents_in_text = len(sent_tokenize(text))
    try:
        onesent = summarize(text, ratio = 1.0 / num_sents_in_text)
    except TypeError:
        try:
            return sent_tokenize(text)[1]
        except IndexError:
            return text
    except ValueError:
        return text 
    if onesent == '':
        onesent = summarize(text, ratio = (1.0 / num_sents_in_text + 0.02))
    return onesent

def removeDuplicatedXandY(x_text, y):
    x_text_nodup, y_nodup = [], []
    for id in xrange(len(x_text)):
        elem = x_text[id]
        if elem not in x_text[id+1:]:
            x_text_nodup.append(elem)
            y_nodup.append(y[id])
    return x_text_nodup, y_nodup

def extractSentencesFromText(title, text, gene, variant=None, protein=None, disease=None):
    # gene_variant   e.g., c.-621G>A|c.116G>A|c.-1399G>A
    # protein        e.g., R222Q|R223Q
    # disease        e.g., aa|bb
    try:
	sents = sent_tokenize(text)
    except UnicodeDecodeError:
	sents = sent_tokenize(text.decode('utf8'))
    # Generate search keywords to extract key sentences from sent
    # Notice in the re expression, it includes '-' [-0-9]
    gene_variants = re.findall(r'[a-z]\.[-0-9]{1,10}', variant) if variant else [] 
    if protein:
        protein = protein.split('.')[-1]
        proteins = getProteinSynonyms(protein)
	proteins = [_.replace('*', '') for _ in proteins]
    else:
	proteins = []
    diseases = disease.split('|') if disease else []
    keywords_genes = [gene] + gene_variants + proteins
    keywords_diseases = diseases
    keywords_genes = [_ for _ in keywords_genes if _ != '']
    keywords_diseases = [_ for _ in keywords_diseases if _ != '']
    search_keywords = list(set(keywords_genes + keywords_diseases))
    keysents = []
    for sent in sents:
	if keywordSearch(search_keywords, sent):
	    keysents.append(sent)
    try:
	summarizeonesent = summarize2OneSent(text)
    except UnicodeDecodeError:
	summarizeonesent = summarize2OneSent(text.decode('utf8'))
    keysents.append(summarizeonesent)
    keysents.append(sents[-1])
    keysents.append(title)
    keysents = filterSelectedSentences(keysents, keywords_genes, keywords_diseases)
    try:
        for sent in keysents:
	    len_sent.append(len(sent.split(' ')))
    except NameError:
        pass

    ## remove () and everything inside 
    keysents_tmp = []
    for sent in keysents:
        loop = 0
        while ('(' in sent or ')' in sent) and loop < 5:
            sent = re.sub(r'\([^()]*\)', '', sent)
            loop += 1
        keysents_tmp.append(sent)
    keysents = keysents_tmp
    keysents = [clean_str(sent) for sent in keysents]
    try:
        search_keywords_list.append(search_keywords)
        len_keysents.append(len(keysents))
    except NameError:
        pass
    return keysents

def load_data_and_labels(data_file, delimiter):
    data = pd.read_csv(data_file, sep=delimiter, dtype=object, na_values=[''], keep_default_na=False)
    data.fillna('', inplace = True)
    labels = pd.unique(data['description'].values).tolist()
    if len(labels) == 5:
        label_map = {
                 'Pathogenic':[0, 0, 0, 0, 1],
                 'Likely pathogenic':[0, 0, 0, 1, 0],
                 'Uncertain significance':[0, 0, 1, 0, 0],
                 'Likely benign':[0, 1, 0, 0, 0],
                 'Benign':[1, 0, 0, 0, 0]
                 }
    elif len(labels) == 2:
        label_map = {
                 'Pathogenic':[0, 1],
                 'Benign':[1, 0]
                 }
    elif len(labels) == 3 or len(labels) == 1:
        label_map = {
                 'Pathogenic':[0, 0, 1],
                 'Uncertain significance':[0, 1, 0],
                 'Benign':[1, 0, 0]
                 }

    global len_sent, len_keysents, search_keywords_list
    len_sent = []
    len_keysents = [] 
    y, x_text = [], []
    search_keywords_list = [] 
    for index, row in data.iterrows():
        if len(labels) in [1, 2, 3, 5]:
            label = row['description']
            title = row['Title']
            text = row['Abstract']
            gene = row['gene']
            variant = row['gene_variant'] # e.g., c.-621G>A|c.116G>A|c.-1399G>A
            protein = row['protein'] # e.g., R222Q|R223Q
            disease = row['disease']

            keysents = extractSentencesFromText(title, text, gene, variant, protein, disease)
             
        # join phrase which has multiple words, e.g., liver cancer ---> liver-cancer
        label = label_map[label]
        y.append(label)
        x_text.append(keysents)  # x_text is a list of lists, keysents is a list of strings

    # Remove duplicates from dataset
    x_text, y = removeDuplicatedXandY(x_text, y)    

    tmp = copy.copy(x_text)
    tmp.sort(key=lambda s: len(s), reverse=True)
    tmp = sum(tmp, []) 
    tmp.sort(key=lambda s: len(s), reverse=True)
    y_array = np.array(y)
    len_keysents = np.array(len_keysents)
    #print np.mean(len_keysents), np.max(len_keysents), np.min(len_keysents), np.std(len_keysents)
    len_sent = np.array(len_sent)
    #print np.mean(len_sent), np.max(len_sent), np.min(len_sent), np.std(len_sent)
    #print y_array.shape 
    return (x_text, y_array)


def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data)-1)/batch_size) + 1
    for epoch in range(num_epochs):
        print epoch
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]


