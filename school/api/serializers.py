from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from school import models as school_models


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = school_models.FormModel
        fields = ['id', 'name']
        extra_kwargs = {'id': {'read_only': True}}


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = school_models.SubjectModel
        fields = ['id', 'name', 'description']
        extra_kwargs = {'id': {'read_only': True}}


class ListRetrieveUnitSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = school_models.UnitModel
        fields = ['id', 'name', 'amount']
        extra_kwargs = {'id': {'read_only': True}}

    def get_amount(self, obj):
        try:
            amount = obj.unit_amounts.first().amount
            return amount
        except Exception as e:
            return None


class ListTopicSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()
    subject = SubjectSerializer()
    form = FormSerializer()
    subtopics = ListRetrieveUnitSerializer(source='topic_units', many=True)

    class Meta:
        model = school_models.TopicModel
        fields = ['id', 'name', 'amount', 'subject', 'form', 'subtopics']
        extra_kwargs = {'id': {'read_only': True}}

    def get_amount(self, obj):
        try:
            return obj.topic_amounts.first().amount
        except Exception as e:
            return None


class RetrieveTopicSerializer(ListTopicSerializer):
    units = serializers.SerializerMethodField()

    class Meta(ListTopicSerializer.Meta):
        fields = ListTopicSerializer.Meta.fields + ['units']

    @staticmethod
    def get_units(obj):
        units = obj.topic_units.all()
        return [{"id": unit.id, "name": unit.name} for unit in units]


class TopicSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, trim_whitespace=True)
    subject = serializers.UUIDField(required=True)
    form = serializers.UUIDField(required=True)

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=school_models.TopicModel.objects.all(),
                fields=['name', 'subject', 'form']
            )
        ]

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


class UnitSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, trim_whitespace=True)
    topic = serializers.UUIDField(required=True)

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=school_models.UnitModel.objects.all(),
                fields=['name', 'topic']
            )
        ]

    def validate(self, obj):
        try:
            topic = school_models.TopicModel.objects.get(id=obj['topic'])
        except school_models.TopicModel.DoesNotExist:
            raise serializers.ValidationError("Topic does not exist")

        obj['topic'] = topic
        return obj


class UpdateUnitSerializer(UnitSerializer):
    request_id = serializers.UUIDField(required=True)


class ListRetrieveVideoSerializer(serializers.ModelSerializer):
    unit = UnitSerializer()

    class Meta:
        model = school_models.VideoModel
        fields = ['id', 'videoid', 'unit', 'label', 'index']
        extra_kwargs = {'id': {'read_only': True}}


class CreateVideoSerializer(serializers.Serializer):
    video = serializers.FileField(required=True)
    unit = serializers.UUIDField(required=True)
    label = serializers.CharField(required=True)
    index = serializers.IntegerField(min_value=0)

    def validate(self, obj):
        try:
            unit = school_models.UnitModel.objects.get(id=obj['unit'])
        except school_models.UnitModel.DoesNotExist:
            raise serializers.ValidationError("Unit does not exist")

        obj.update({"unit": unit})
        return obj


class UpdateVideoSerializer(CreateVideoSerializer):
    request_id = serializers.UUIDField(required=True)
