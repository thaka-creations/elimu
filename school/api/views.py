import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from school.api import serializers as school_serializers
from school import models as school_models


def valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = school_models.SubjectModel.objects.all()
    serializer_class = school_serializers.SubjectSerializer

    @staticmethod
    def create(request):
        payload_serializer = school_serializers.SubjectSerializer(
            data=request.data, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data
        school_models.SubjectModel.objects.create(**validated_data)
        return Response({"details": "Subject created successfully"}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def update_subject(self, request):
        payload = request.data
        request_id = payload.pop("request_id")
        payload_serializer = school_serializers.SubjectSerializer(
            data=payload, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data

        try:
            instance = school_models.SubjectModel.objects.get(id=request_id)
        except school_models.SubjectModel.DoesNotExist:
            return Response({"details": "Subject does not exist"})

        for k, v in validated_data.items():
            if hasattr(instance, k):
                setattr(instance, k, v)

        instance.save()

        return Response({"details": "Subject updated successfully"}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def retrieve_subject(self, request):
        request_id = request.query_params.get('request_id', False)

        is_valid = valid_uuid(request_id)

        if not is_valid:
            return Response({"details": "request id is required or is not valid"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = school_models.SubjectModel.objects.get(id=request_id)
        except school_models.SubjectModel.DoesNotExist:
            return Response({"details": "Subject does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = school_serializers.SubjectSerializer(
            instance
        )
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)


class FormViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = school_models.FormModel.objects.all()
    serializer_class = school_serializers.FormSerializer

    @staticmethod
    def create(request):
        serializer = school_serializers.FormSerializer(
            data=request.data, many=False
        )

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        school_models.FormModel.objects.create(**validated_data)
        return Response({"details": "Form created successfully"}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def update_form(self, request):
        try:
            request_id = request.data.pop("request_id")
        except Exception as e:
            return Response({"details": e}, status=status.HTTP_400_BAD_REQUEST)

        payload_serializer = school_serializers.FormSerializer(data=request.data, many=False)

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data

        try:
            instance = school_models.FormModel.objects.get(id=request_id)
        except school_models.FormModel.DoesNotExist:
            return Response({"details": "Form does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        for k, v in validated_data.items():
            if hasattr(instance, k):
                setattr(instance, k, v)

        instance.save()
        return Response({"details": "Form updated successfully"}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def retrieve_form(self, request):
        request_id = request.query_params.get("request_id", False)
        is_valid = valid_uuid(request_id)

        if not is_valid:
            return Response({"details": "request id is required or is not valid"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = school_models.FormModel.objects.get(id=request_id)
        except school_models.FormModel.DoesNotExist:
            return Response({"details": "Form does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = school_serializers.FormSerializer(instance)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)


class UnitViewSet(viewsets.ViewSet):

    @staticmethod
    def list(request):
        """
        for form and subject
        list units for form and subject
        """
        form = request.query_params.get('form', False)
        subject = request.query_params.get('subject', False)

        if not form and not subject:
            return Response({"details": "Form and subject are required"}, status=status.HTTP_400_BAD_REQUEST)

        qs = school_models.UnitModel.objects.filter(subject__id=subject, form__id=form)
        serializer = school_serializers.ListRetrieveUnitSerializer(qs, many=True)

        return Response({"details": serializer}, status=status.HTTP_200_OK)

    @staticmethod
    def create(request):
        """
        add unit
        """
        payload = request.data
        payload_serializer = school_serializers.UnitSerializer(
            data=payload, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data
        school_models.UnitModel.objects.create(**validated_data)

        return Response({"details": "Unit created successfully"}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def retrieve_unit(self, request):
        request_id = request.query_params.get("request_id", False)
        is_valid = valid_uuid(request_id)

        if not is_valid:
            return Response({"details": "request id is required or is not valid"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = school_models.UnitModel.objects.get(id=request_id)
        except school_models.UnitModel.DoesNotExist:
            return Response({"details": "Unit does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = school_serializers.ListRetrieveUnitSerializer(instance)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def update_unit(self, request):
        """
        depends on payload passed to update unit
        """
        payload = request.data
        payload_serializer = school_serializers.UpdateUnitSerializer(
            data=payload, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data
        request_id = validated_data.pop("request_id")

        try:
            instance = school_models.UnitModel.objects.get(id=request_id)
        except school_models.UnitModel.DoesNotExist:
            return Response({"details": "Unit does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        for k, v in validated_data:
            instance.k = v
            instance.save()

        return Response({"details": "Unit updated successfully"}, status=status.HTTP_200_OK)


class VideoViewSet(viewsets.ViewSet):

    @staticmethod
    def create(request):
        """
        add video , url and unit required
        """
        payload = request.data
        payload_serializer = school_serializers.CreateVideoSerializer(
            data=payload, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data
        school_models.VideoModel.objects.create(**validated_data)

        return Response({"details": "Video added successfully"}, status=status.HTTP_200_OK)

    @staticmethod
    def list(request):
        """
        list videos for a given unit
        """
        unit = request.query_params.get("unit", False)
        qs = school_models.VideoModel.objects.filter(unit__id=unit)
        serializer = school_serializers.ListRetrieveVideoSerializer(qs, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def retrieve_video(self, request):
        """
        retrieve video
        """
        request_id = request.query_params.get("request_id", False)
        is_valid = valid_uuid(request_id)

        if not is_valid:
            return Response({"details": "request id is required or is not valid"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = school_models.VideoModel.objects.get(id=request_id)
        except school_models.VideoModel.DoesNotExist:
            return Response({"details": "Video does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = school_serializers.ListRetrieveVideoSerializer(instance)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def update_video(self, request):
        """
        update video
        """
        payload = request.data
        payload_serializer = school_serializers.UpdateVideoSerializer(
            data=payload, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data
        request_id = validated_data.pop("request_id")

        try:
            instance = school_models.VideoModel.objects.get(id=request_id)
        except school_models.VideoModel.DoesNotExist:
            return Response({"details": "Video does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        for k, v in validated_data:
            instance.k = v
            instance.save()

        return Response({"details": "Video updated successfully"}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def delete_video(self, request):
        pass
