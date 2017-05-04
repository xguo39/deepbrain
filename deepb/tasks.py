from celery.decorators import task
from celery.utils.log import get_task_logger

from main import master_function
from deepb.models import Main_table, Raw_input_table
from django.utils import timezone
import pandas as pd


logger = get_task_logger(__name__)


@task(name="trigger_background_main_task")
def trigger_background_main_task(raw_input_id):
    """sends an email when feedback form is filled successfully"""
    logger.info("Start background main task")
    ACMG_result, df_genes, phenos, field_names = master_function(raw_input_id)

    input_gene = df_genes.to_json(orient='records')
    input_phenotype = ', '.join(phenos)
    result_table = ACMG_result.to_json(orient='records')

    logger.info("Finish processing data, start writing data to DB in background main task")

    raw_input = Raw_input_table.objects.get(id=raw_input_id)

    sample = Main_table(
        task_id=raw_input_id,
        input_gene=input_gene,
        input_phenotype=input_phenotype,
        result=result_table,
        pub_date=timezone.now(),
        user_name=raw_input.user_name,
        task_name=raw_input.task_name,
    )
    sample.save()
    
    logger.info("Finish writing data to DB in background main task")