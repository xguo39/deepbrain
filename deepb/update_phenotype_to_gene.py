import pandas as pd
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def getGeneVariants(final_res, gene):
    gene_variants = []
    for item in final_res:
        if item[0] == gene:
            gene_variants.append(item[1])
    return gene_variants


def rankGenePhenoByCodingEffect(final_res, variants, ranking_genes):
    '''
    final_res (list): [(gene, variant, protein), ...]
    variants (dict): {(gene, variant):{}, ...}
    ranking_genes (list): [(gene, score, hits, pheno_specificity_score), ...]

    '''
    critical_coding_effects = ["chromosome", "exon_loss", "frameshift", "inversion", "feature_ablation", "gene_fusion", "rearranged_at_DNA_level", "initiator_condon", "splice_acceptor", "splice_donor", "stop_gain", 'start_lost', 'stop_lost']

    updated_ranking_genes = []
    for data in ranking_genes:
        gene, score_sim, hits, score = data    
        gene_variants = getGeneVariants(final_res, gene)
        coding_effects = []
        for variant in gene_variants:
            try:
                effect = variants[(gene, variant)]['effect'] 
                effect_is_critical = re.search('|'.join(critical_coding_effects), effect, re.I)
                if effect_is_critical:
                    coding_effects.append(1)
                else:
                    coding_effects.append(0)
            except KeyError:
                continue

        # For every critical coding effect of variant for a gene, add 0.5 to the score
        coding_effect_score = 0.5 * sum(coding_effects)
        score = float(score) + coding_effect_score
        updated_ranking_genes.append((gene, score_sim, hits, score)) 
    return updated_ranking_genes


def getRecessiveDominantGenes():
    df_omim_mim2gene = pd.read_csv(os.path.join(BASE, 'data/ACMG/omim_mim2gene.txt'), sep = '\t', skiprows = 1, usecols = [0, 1, 3], names = ['mim', 'type', 'gene'])
    df_mim_dominant = pd.read_csv(os.path.join(BASE, 'data/ACMG/mim_domin.txt'), names = ['mim'])
    df_mim_recessive = pd.read_csv(os.path.join(BASE, 'data/ACMG/mim_recessive.txt'), names = ['mim'])
    df_mim_dominant = df_mim_dominant.merge(df_omim_mim2gene, how = 'left', on = 'mim')
    df_mim_recessive = df_mim_recessive.merge(df_omim_mim2gene, how = 'left', on = 'mim')
    dominant_genes = pd.unique(df_mim_dominant.gene.values).tolist()
    recessive_genes = pd.unique(df_mim_recessive.gene.values).tolist()
    return dominant_genes, recessive_genes

        
def rankGenePhenoByInheritancePattern(ranking_genes, gene_zygosity, candidate_vars):
    dominant_genes, recessive_genes = getRecessiveDominantGenes()
    gene2variants = dict()
    variantid2genevariant = dict()
    for var in candidate_vars:
        gene, variant, transcript, variant_id = var
        if gene not in gene2variants:
            gene2variants[gene] = [variant]
        else:
            gene2variants[gene].append(variant)
        variantid2genevariant[variant_id] = (gene, variant)

    for key in gene_zygosity.keys():
        if key in variantid2genevariant:
            gene, variant = variantid2genevariant[key]
            gene_zygosity[(gene, variant)] = gene_zygosity[key]

    updated_ranking_genes = []
    for data in ranking_genes: 
        gene, score_sim, hits, score = data
        gene_is_dominant, gene_is_recessive = False, False
        if gene in dominant_genes:
            gene_is_dominant = True
        if gene in recessive_genes:
            gene_is_recessive = True
        variants = gene2variants[gene]
        for variant in variants:
            if (gene, variant) in gene_zygosity: 
                zygosity = gene_zygosity[(gene, variant)]
                inheritance_pattern_score = 0.0
                if gene_is_dominant and not gene_is_recessive:
                    if re.match(r'de ', zygosity, re.I): inheritance_pattern_score = 0.5 
                    if re.match(r'hem', zygosity, re.I): inheritance_pattern_score = 0.25 
                    if re.match(r'hom|comp', zygosity, re.I): inheritance_pattern_score = 0.1 
                    if re.match(r'het', zygosity, re.I): inheritance_pattern_score = 0.0
                elif not gene_is_dominant and gene_is_recessive:
                    if re.match(r'hom|comp', zygosity, re.I): inheritance_pattern_score = 0.5 
                    if re.match(r'de |hem', zygosity, re.I): inheritance_pattern_score = 0.25 
                    if re.match(r'het', zygosity, re.I): inheritance_pattern_score = 0.0
                score = float(score) + inheritance_pattern_score
                updated_ranking_genes.append((gene, variant, score_sim, hits, score, zygosity))
    # Noew updated_ranking genes has one more column: variant
    return updated_ranking_genes
 
