from celery.decorators import task
from celery.utils.log import get_task_logger

from main import master_function
from deepb.models import Main_table
from django.utils import timezone
import pandas as pd


logger = get_task_logger(__name__)


@task(name="trigger_background_main_task")
def trigger_background_main_task(phenotype_file_path, gene_file_path, id):
    """sends an email when feedback form is filled successfully"""
    logger.info("Start background main task")
    ACMG_result, df_genes, phenos = master_function(phenotype_file_path, gene_file_path)

    df_genes.columns = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6']
    input_gene = df_genes.to_json(orient='records')[1:-1].replace('},{', '} {')
    input_phenotype = ', '.join(phenos)
    result_table = ACMG_result.to_json(orient='records')[1:-1].replace('},{', '} {')
    # pub_date = timezone.now()

    logger.info("Finish processing data, start writing data to DB in background main task")

    sample = Main_table(
        task_id=id,
        input_gene=input_gene,
        input_phenotype=input_phenotype,
        result=result_table,
        pub_date=timezone.now()
    )
    sample.save()
    
    logger.info("Finish writing data to DB in background main task")