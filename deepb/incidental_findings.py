import pickle

incidental_genes_phenos = dict()

with open('data/incidental_findings.csv', 'rb') as f:
    f.readline()
    for line in f:
        line = line.rstrip()
        parts = line.split('\t')
        pheno = parts[0]
        genes = parts[1:]
        for gene in genes:
            if gene not in incidental_genes_phenos:
                incidental_genes_phenos[gene] = [pheno]
            else:
                incidental_genes_phenos[gene].append(pheno)

print incidental_genes_phenos

outfile = open('data/incidental_findings_genes.p', 'wb')
pickle.dump(incidental_genes_phenos, outfile)

