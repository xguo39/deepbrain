from rest_framework import serializers
from deepb.models import Main_table, Raw_input_table

class Progress_task_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Raw_input_table
        fields = ('id','task_name','pub_date','status','process_time')


class All_task_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Raw_input_table
        fields = ('id','task_name','pub_date','status','checked')


class Evaluated_task_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Raw_input_table
        fields = ('id','task_name','pub_date','status')