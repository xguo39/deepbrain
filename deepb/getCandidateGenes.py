import pandas as pd
import pickle
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def gethposuperclass():
    global hpo_superclass
    hpo_superclass = dict()
    HPO_SUPERCLASSES = os.path.join(BASE, "data/hpo_superclasses.txt")
    with open(HPO_SUPERCLASSES, 'rb') as f:
        f.readline()
        for line in f:
            line = line.rstrip()
            parts = line.split('\t')
            hpoid = parts[0]
            superclasses = parts[1].strip('[]').replace("'", "")
            superclasses = [_.strip() for _ in superclasses.split(',')]
            hpo_superclass[hpoid] = superclasses

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

def getCandidateGenes(gene_associated_phenos, gene_associated_pheno_hpoids, variants):
    infile = open(os.path.join(BASE, 'data/jax_phenotypes.p'), 'rb')
    associated_genes, jax_gene_key_phenos = pickle.load(infile)
    infile.close()
    gethposuperclass()
    jax_candidate_genes = []

    for key in variants.keys():
        gene, variant = key
        zygosity = variants[key]['zygosity']
        coding_effect = variants[key]['effect']
        maf_exac = variants[key]['maf_exac']

        if gene not in gene_associated_phenos or gene_associated_phenos[gene]:
            continue
        if not re.match(r'hom|hem|de |comp', zygosity, re.I):
            continue
        null_variant_types = ["frameshift", "splice_acceptor", "splice_donor", "stop_gain", 'start_lost', 'stop_lost']
        if not re.search('|'.join(null_variant_types), coding_effect, re.I):
            continue
        if maf_exac and float(maf_exac) >= 0.001:
            continue

        pheno_hpoids = gene_associated_pheno_hpoids[gene]
        in_candidate_genes = False
        for hpoid in pheno_hpoids:
            hpoid_parents =  getAllAncestorsBFS(hpoid, hpo_superclass) 
            for parent_hpoid in hpoid_parents:
                # if the parent of the current hpoid is in jax pheno associated genes, and the current gene is one of the jax genes associated with the pheno, then the current gene is among candidate genes
                if parent_hpoid in associated_genes and gene in associated_genes[parent_hpoid]:
                    jax_candidate_genes.append(gene)
                    in_candidate_genes = True
                    break
            if in_candidate_genes:
                break 
    return jax_candidate_genes, jax_gene_key_phenos

