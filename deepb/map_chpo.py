# -*- coding: utf-8 -*-

import sys
import os
from main import read_input_pheno_file
from map_phenotype_to_gene import map2hpoWithPhenoSynonyms
import pandas as pd

reload(sys)
sys.setdefaultencoding('utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
CHPO = os.path.join(BASE, "data/chpo.2016-10.xls")

def map_chpo(chinese_pheno):
    # try:
    phenos, corner_cases, original_phenos, phenotype_translate = read_input_pheno_file(chinese_pheno)
    match_result = map2hpoWithPhenoSynonyms(phenotype_translate)
    match_result = sorted(match_result, key = lambda x: x[2], reverse = True)

    if match_result[0][0] == 'Familial  hyperprolactinemia':
        match_result = ''
    else:
        chpo = pd.read_excel(CHPO)
        chpo.columns = ['类别','HPO编号','表型英文名','表型中文名','英文释义','释义']
        if match_result[0][2] == 1.0:
            match_result = match_result[:1]
        match_id = [i[1] for i in match_result]
        for indx,i in enumerate(match_id):
            if i[-7:]=='synonym':
                match_id[indx] = match_id[indx][:-8]
        match_table = chpo[chpo['HPO编号'].isin(match_id)].iloc[:5,[3,2,1,0,5]].reset_index(drop=True)
        # match_result = match_table.values.tolist()
        match_result = match_table.to_json(orient='records')

    # except:
    #     match_result = ['无匹配']

    return match_result