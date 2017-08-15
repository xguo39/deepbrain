from rest_framework import serializers
from deepb.models import Main_table, Raw_input_table

# class New_task_Serializer(serializers.ModelSerializer):

#     class Meta:
#         model = Raw_input_table
#         fields = ('task_name', 'pub_date', 'status', 'process_time')

#     def create(self, validated_data):
#         raw_input_gene = validated_data.get('gene_file', None)

#         phenotype_type = ''
#         phenotype_file = ''
#         try:
#             phenotype_file = request.FILES['symptom_file']   
#         except:
#             phenotype = ''
#         phenotype_type = request.POST.get('input_text_phenotype', None)

#         if phenotype_type:
#             phenotype = phenotype_type
#         if phenotype_file:
#             phenotype = phenotype_file.read()

#         if validated_data.get('input_phen', None):
#             input_pheno = validated_data.get('input_phen', None)
#         elif validated_data.get('input_text_phenotype', None):
#             input_pheno = validated_data.get('input_text_phenotype', None)
#         else:
#             input_pheno = ''

#         raw_input_phenotype = input_pheno
#         user_name = validated_data.get('title', None)
#         task_name = validated_data.get('title', None)
#         title = validated_data.get('title', None)
#         article = validated_data.get('article', None)
#         tags = validated_data.get('tags', None)
#         date = validated_data.get('date', None)
#         user = self.context.get("user")
#         return Post.objects.create(title=title, author=user, tags=tags, article=article, date=date)


class Progress_task_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Raw_input_table
        fields = ('id','task_name','pub_date','status','process_time')


class All_task_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Raw_input_table
        fields = ('id','task_name','pub_date','status','checked')

class Case_result_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Main_table
        fields = ('task_name', 'result', 'interpretation_chinese', 'input_gene','input_phenotype')


