from rest_framework import serializers
from deepb.models import Main_table, Raw_input_table

class New_task_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Raw_input_table
        fields = ('task_name', 'pub_date', 'status', 'process_time')

    def create(self, validated_data):
        raw_input_gene = validated_data.get('title', None)
        raw_input_phenotype = validated_data.get('title', None)
        user_name = validated_data.get('title', None)
        task_name = validated_data.get('title', None)
        title = validated_data.get('title', None)
        article = validated_data.get('article', None)
        tags = validated_data.get('tags', None)
        date = validated_data.get('date', None)
        user = self.context.get("user")
        return Post.objects.create(title=title, author=user, tags=tags, article=article, date=date)


class Progress_task_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Raw_input_table
        fields = ('id','task_name','status','process_time')


class All_task_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Raw_input_table
        fields = ('id','task_name','pub_date','status','process_time')

class Case_result_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Main_table
        fields = ('task_name', 'result', 'interpretation_chinese', 'input_gene','input_phenotype')


# {
#  id:"myForm",
#  name:"myForm",
#  encType:"multipart/form-data",
#  input:{
#   task_name: text,
#   gene_file: file(.txt,.xlsx,.xls,.csv,.vcf),
#   input_phen: file(.txt),
#   input_text_phenotype:text,
#   father_check:boolean,
#   father_check_pheno:boolean,
#   father_gene_file:file(.txt,.xlsx,.xls,.csv,.vcf),
#   mother_check:boolean,
#   mother_check_pheno:boolean,
#   mother_gene_file:file(.txt,.xlsx,.xls,.csv,.vcf),
#   check_incidental_findings:boolean,
#   check_candidate_genes:boolean
# }