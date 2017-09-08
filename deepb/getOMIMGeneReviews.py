import pickle

omim_gene_reviews_name = dict()

with open('data/NBKid_shortname_OMIM.txt', 'rb') as f:
    f.readline()
    for line in f:
        line = line.rstrip()
        parts = line.split('\t')
        GR_shortname, omim = parts[1], parts[2]
        omim_gene_reviews_name[omim] = GR_shortname

outfile = open('data/omim_genereviews.p', 'wb')
pickle.dump(omim_gene_reviews_name, outfile)
outfile.close()

