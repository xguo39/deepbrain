from bs4 import BeautifulSoup
import os
import pickle
import re

files = [f for f in os.listdir('/media/sf_sharedfolder/gene_NBK1116') if 'nxml' in f]
gr_shortname_penetrance = dict()
#num = 0
for f in files:
    #num += 1
    #if num >= 20:  
    #    break
    gr_shortname = f.split('.')[0]
    soup = BeautifulSoup(open(os.path.join('/media/sf_sharedfolder/gene_NBK1116', f)), 'lxml')
    try:
        penetrance = soup.find_all(text='Penetrance')[0].findNext().get_text()
    except IndexError:
        pass
    gr_shortname_penetrance[gr_shortname] = penetrance

#print len(gr_shortname_penetrance.keys())

#print gr_shortname_penetrance

#outfile = open('data/gr_shortname_penetrance.p', 'wb')
#pickle.dump(gr_shortname_penetrance, outfile)
#outfile.close()

complete_penetrance_gr_shortnames, incomplete_penetrance_gr_shortnames = [], []
for gr_shortname in gr_shortname_penetrance.keys():
    text = gr_shortname_penetrance[gr_shortname]
    if re.search(r'\bcomplete\b|\bcompletely\b|\bfull\b|\bfully\b', text, re.I) or (re.search(r'100%|100 %', text) and not re.search(r'\b[0-9]{2}%|\b[0-9]{2} %', text)):
        complete_penetrance_gr_shortnames.append(gr_shortname) 
    else:
        incomplete_penetrance_gr_shortnames.append(gr_shortname)

outfile = open('data/gr_shortname_penetrance_lists.p', 'wb')
pickle.dump([complete_penetrance_gr_shortnames, incomplete_penetrance_gr_shortnames], outfile)
outfile.close()


