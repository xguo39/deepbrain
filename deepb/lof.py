# -*- coding: utf-8 -*-

import sys
import os
from google import google

reload(sys)
sys.setdefaultencoding('utf-8')

lof = 0

def check_lof(input_gene):
    lof_result = []
    lof = 0
    search_results = google.search(input_gene.upper()+' loss of function', 1)
    for i in search_results:
        for j in i.description.split("..."):
            j = j.replace("\n", "")
            if ('loss-of-function ' in j or ' loss of function 'in j or ' Loss of function 'in j) and (input_gene in j) and (('no' and 'not' and 'whether') not in j):
                lof = 1
                lof_result.append(i)
                break
        else:
            continue
    if lof == 1:
        return 1, lof_result
    else:
        return 2, lof_result
