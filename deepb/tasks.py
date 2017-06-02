from celery.decorators import task
from celery.utils.log import get_task_logger

from main import master_function
from deepb.models import Main_table, Raw_input_table
from django.utils import timezone
import pandas as pd
import time


logger = get_task_logger(__name__)


@task(name="trigger_background_main_task")
def trigger_background_main_task(raw_input_id):
    """sends an email when feedback form is filled successfully"""
    logger.info("Start background main task")
    raw_input = Raw_input_table.objects.get(id=raw_input_id)
    try:
        start_point = time.time()
        ACMG_result, df_genes, phenos, field_names, variant_ACMG_interpretation, variant_ACMG_interpret_chinese = master_function(raw_input_id)

        input_gene = df_genes.to_json(orient='records')
        input_phenotype = ', '.join(phenos)
        result_table = ACMG_result.to_json(orient='records')
        interpretation = variant_ACMG_interpretation.to_json(orient='records')
        interpretation_chinese = variant_ACMG_interpret_chinese.to_json(orient='records')


        logger.info("Finish processing data, start writing data to DB in background main task")

        
        sample = Main_table(
            task_id=raw_input_id,
            input_gene=input_gene,
            input_phenotype=input_phenotype,
            result=result_table,
            interpretation=interpretation,
            interpretation_chinese=interpretation_chinese,
            pub_date=timezone.now(),
            user_name=raw_input.user_name,
            task_name=raw_input.task_name,
        )
        sample.save()
        logger.info("Finish writing data to DB in background main task")
        raw_input.status = "succeed"
        raw_input.process_time = (time.time()-start_point)/60
        raw_input.save()

    except:
        raw_input.status = raw_input.status + " failed"
        raw_input.save()
        logger.info("Failed")





    