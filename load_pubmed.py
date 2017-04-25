import django
django.setup()

from deepb.models import pubmed

with open('pubmed_data_variantnotnull.txt', 'rb') as f:
	for line in f.readlines():
		line = line.rstrip()
		parts = line.split('\t')
		gene = part[0]
		protein_variant = part[1]
		pmid = part[2]
		title = part[3]
		journal = part[4]
		year = part[5]
		month = part[6]
		impact_factor = part[7]
		abstract = part[8]
		variant_id = part[9]
		protein_domain = part[10]
		p = pubmed(
			gene=gene, 
			protein_variant=protein_variant,
			pmid=pmid,
			title=title,
			journal=journal,
			year=year,
			month=month,
			impact_factor=impact_factor,
			abstract=abstract,
			variant_id=variant_id,
			protein_domain=protein_domain
			)
		p.save