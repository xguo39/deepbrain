
import pandas as pd
import pickle

'''
df = pd.read_csv('data/parsed_clinvar.txt', sep = '\t', usecols = [7, 8])
print df.head()
print df.shape
df = df[df.disease.notnull() & df.disease_prevalence.notnull()]
print df.shape
print df.head()
df.drop_duplicates(inplace = True)
print df.shape
print df.head()
df.sort_values(by='disease', ascending = 1, inplace = True)
df.to_csv('/tmp/disease_prevalence.txt', index = False, sep = '\t')

prevalence_list = []
with open('/tmp/disease_prevalence.txt', 'rb') as f:
    f.readline()
    for line in f:
        line = line.rstrip()
        disease, prevalence = line.split('\t')
        prevalences = prevalence.split('|')
        prevalence_list += prevalences
prevalence_list = list(set(prevalence_list))

df = pd.Series(prevalence_list)
df.sort_values(inplace = True)
df.to_csv('/tmp/prevalence_list.txt', index = False, sep = '\t') 
'''

df = pd.read_csv('/media/sf_sharedfolder/clean_prevalence_list.txt', sep = '\t')
prevalence_numerical_value = df.set_index('prevalence').to_dict()['numerical_prevalence']
#print prevalence_numerical_value
print df

disease_to_prevalence = dict()
with open('/tmp/disease_prevalence.txt', 'rb') as f:
    f.readline()
    for line in f:
        line = line.rstrip()
        disease, prevalence = line.split('\t')
        diseases = disease.split('|')
        prevalences = prevalence.split('|')
        for i in xrange(0, len(diseases)):
            try:
                #print diseases[i], prevalences[i]
                if 'the population of infertile, but otherwise healthy' in prevalences[i]:
                    print prevalences[i], prevalence_numerical_value[prevalences[i]]
                disease_to_prevalence[diseases[i].lower()] = prevalence_numerical_value[prevalences[i]]
            except:
                continue

outfile = open('data/disease_prevalence.p', 'wb')
pickle.dump(disease_to_prevalence, outfile)
outfile.close()
print disease_to_prevalence

