from rest_framework import serializers
from school import models as school_models


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = school_models.FormModel
        fields = ['id', 'name']
        extra_kwargs = {'id': {'read_only': True}}

    def validate(self, obj):
        qs = school_models.FormModel.objects.filter(name=obj['name'])
        if qs.exists():
            raise serializers.ValidationError("Form exists")
        return obj


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = school_models.SubjectModel
        fields = ['id', 'name', 'description']
        extra_kwargs = {'id': {'read_only': True}}

    def validate(self, obj):
        qs = school_models.SubjectModel.objects.filter(name=obj['name'])
        if qs.exists():
            raise serializers.ValidationError("Subject exists")
        return obj
