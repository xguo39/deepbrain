import myvariant
import re
import pandas as pd
import amino_acid_mapping

df = pd.read_csv('updatefiles_parsed_file', sep = '|', usecols=[0,1,2], dtype = str)
df = df[df.protein_variant.notnull()]
df['protein_variant'] = df['protein_variant'].str.lstrip('(')
df.loc[~df.protein_variant.str.contains('\)'), 'protein_variant'] = df.loc[~df.protein_variant.str.contains('\)'), 'protein_variant'].str.replace('(', '')

mv = myvariant.MyVariantInfo()
snpeff_data = dict() 

def collectSnpeff(gene, protein_variant, key):
    global snpeff_data

    if key == 'variant':
        query = 'snpeff.ann.gene_id:%s AND snpeff.ann.hgvs_c:%s' % (gene, protein_variant)
    else:
        query = 'snpeff.ann.gene_id:%s AND snpeff.ann.hgvs_p:%s' % (gene, protein_variant)

    snpeff = mv.query(query, fields='snpeff')
    snpeff_data[(gene, protein_variant)] = snpeff
 
    try:
        variant_id = snpeff['hits'][0]['_id']
    except IndexError:
        return '', '', '', '' 
    hits = snpeff['hits']
    anns = []
    scores = []
    variant_ids = []
    # There can be multiple hits; scan all hits to find out the variant_id that match gene, variant, and transcript
    for hit in hits:
        try:
            variant_ids.append(hit['_id'])
        except:
            variant_ids.append('')
        try:
            scores.append(hit['_score'])
        except:
            scores.append(0)
        try:
            anns.append(hit['snpeff']['ann'])
        except:
            anns.append('')

    max_score = 0
    for ind in xrange(len(anns)):
        ann = anns[ind]
        tmp_variant_id = variant_ids[ind]
        score = scores[ind]
        if isinstance(ann, dict):
            ann = [ann]
        transcript = transcript.decode('utf-8')
        for var in ann:
            if var['hgvs_c'] == variant and var['gene_id'] == gene:
                if score > max_score:
                    max_score = score 
                    #effect, feature_id, feature_type, putative_impact, transcript_biotype = (var['effect'], var['feature_id'], var['feature_type'], var['putative_impact'], var['transcript_biotype'])
                    feature_id = var['feature_id'] if 'feature_id' in var else ''
                    hgvs_c = var['hgvs_c'] if 'hgvs_c' in var else ''
                    hgvs_p = var['hgvs_p'] if 'hgvs_p' in var else ''
                    variant_id = tmp_variant_id
    return variant_id, hgvs_c, hgvs_p, feature_id

def collectDomain():


protein_map1to3 = amino_acid_mapping.map1to3
re_map1to3 = re.compile('|'.join(protein_map1to3))

variant_ids = []
for index, row in df.iterrows():
    gene = row['gene']
    protein_variant = row['protein_variant']
    pmid = row['pmid']
   
    if re.match(r'c\.|g\.', protein_variant):
        key = 'variant'
    else:
        key = 'protein'

    if key == 'protein':
        if re.match(r'[A-Za-z]{1,3}[0-9]{0,10}$', protein_variant):
            continue
        if not re.match(r'p\.', protein_variant):
            protein_variant = 'p.' + protein_variant
        if re.match(r'p\.[A-Z][0-9]', protein_variant):
            protein_variant = re_map1to3.sub(lambda m: protein_map1to3[m.group(0)], protein_variant)

    variant_id, hgvs_c, hgvs_p = collectSnpeff(gene, protein_variant, key)
    if not variant_id:
        continue

    variant_ids.append(variant_id)
    if len(variant_ids) == 100:
        col


 
 
