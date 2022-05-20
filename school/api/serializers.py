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


class UnitSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    form = FormSerializer()

    class Meta:
        model = school_models.UnitModel
        fields = ['id', 'name', 'subject', 'form']
        extra_kwargs = {'id': {'read_only': True}}


class AddUnitSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, trim_whitespace=True)
    subject = serializers.UUIDField(required=True)
    form = serializers.UUIDField(required=True)

    def validate(self, obj):
        try:
            subject = school_models.SubjectModel.objects.get(id=obj['subject'])
        except school_models.SubjectModel.DoesNotExist:
            raise serializers.ValidationError("Subject does not exist")

        try:
            form = school_models.FormModel.objects.get(id=obj['form'])
        except school_models.FormModel.DoesNotExist:
            raise serializers.ValidationError("Form does not exist")

        obj['subject'] = subject
        obj['form'] = form
        return obj


class VideoSerializer(serializers.ModelSerializer):
    unit = UnitSerializer()

    class Meta:
        model = school_models.VideoModel
        fields = ['id', 'url', 'unit']
        extra_kwargs = {'id': {'read_only': True}}
