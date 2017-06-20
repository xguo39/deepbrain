# -*- coding: utf-8 -*-

import sys
import os
from main import read_input_pheno_file
from map_phenotype_to_gene import map2hpoWithPhenoSynonyms
import pandas as pd
from langdetect import detect
from google import google

reload(sys)
sys.setdefaultencoding('utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
CHPO = os.path.join(BASE, "data/chpo.2016-10.xls")


def smart_match(input_en, chpo):
    search_results = google.search("afraid of light", 1)
    wiki = list(set([i.name[:-12] for i in search_results if i.name[-9:]=='Wikipedia']))
    for i in wiki:
        try:
            wiki_match = chpo[chpo['表型英文名']==i]
            return wiki_match.to_json(orient='records')
        except:
            pass

    match_result = map2hpoWithPhenoSynonyms(input_en)
    match_result = sorted(match_result, key = lambda x: x[2], reverse = True)
    if match_result == []:
        match_result = []
    else:
        if match_result[0][2] == 1.0:
            match_result = match_result[:1]
        match_id = [i[1] for i in match_result]
        for indx,i in enumerate(match_id):
            if i[-7:]=='synonym':
                match_id[indx] = match_id[indx][:-8]
        match_table = chpo[chpo.iloc[:,2].isin(match_id)].iloc[:7,:].reset_index(drop=True)
        match_result = match_table.to_json(orient='records')
    return match_result

def map_chpo(input_pheno):
    try:
        if not input_pheno:
            match_result = ''
        else:
            chpo = pd.read_excel(CHPO)
            chpo.columns = ['类别','HPO编号','表型英文名','表型中文名','英文释义','释义']
            chpo = chpo.iloc[:,[3,2,1,0,5]]
            if detect(unicode(input_pheno)) in ["zh-cn","ko"]:
                direct_match = chpo[chpo['表型中文名']==input_pheno]
                substring_match = [i for i,j in enumerate(list(chpo['表型中文名'])) if input_pheno in j]
                if len(direct_match) > 0:
                    match_result = direct_match.to_json(orient='records')
                elif len(substring_match) > 0:
                    match_table = chpo.iloc[substring_match,:].reset_index(drop=True)
                    match_result = match_table.to_json(orient='records')
                else:
                    phenos, corner_cases, original_phenos, phenotype_translate = read_input_pheno_file(input_pheno)
                    match_result = smart_match(phenotype_translate, chpo)
            else:
                match_result = smart_match(input_pheno, chpo)
    except:
        match_result = []

    return match_result