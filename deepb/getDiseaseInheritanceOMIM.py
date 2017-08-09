import pickle
import re

dominant_diseases, recessive_diseases = [], []
disease2omimid = dict()
with open('data/ACMG/omim_genemap2.txt', 'rb') as f:
    f.readline()
    for line in f:
        line = line.rstrip('\n')
        parts = line.split('\t')
        try:
            phenotypes = parts[12]
        except:
            print parts
        phenos = phenotypes.split(';')
        for pheno in phenos:
            pheno = pheno.lower()
            disease = pheno.split(',')[0]
            disease = disease.replace('{', '')
            disease = disease.replace('}', '')
            disease = disease.replace('[', '')
            disease = disease.replace(']', '')
            disease = disease.replace('?', '')
            disease = disease.strip()
            try:
                omim_id = re.search('[0-9]{6}', pheno).group()
                disease2omimid[disease] = omim_id
            except:
                pass
            if 'autosomal dominant' in pheno:
                dominant_diseases.append(disease)
            if 'autosomal recessive' in pheno:
                recessive_diseases.append(disease)
dominant_diseases = list(set(dominant_diseases))
recessive_diseases = list(set(recessive_diseases))

outfile = open('data/disease_inheritance.p', 'wb')
pickle.dump([dominant_diseases, recessive_diseases], outfile)
outfile.close() 

outfile = open('data/disease2omimid.p', 'wb')
pickle.dump(disease2omimid, outfile)
outfile.close() 


