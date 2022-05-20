from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from school.api import serializers as school_serializers
from school import models as school_models


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = school_models.SubjectModel.objects.all()
    serializer_class = school_serializers.SubjectSerializer


class FormViewSet(viewsets.ModelViewSet):
    queryset = school_models.SubjectModel.objects.all()
    serializer_class = school_serializers.FormSerializer


class UnitViewSet(viewsets.ViewSet):

    @action(methods=['GET'], detail=False)
    def list_units(self, request):
        pass

    @action(methods=['POST'], detail=False)
    def add_unit(self, request):
        pass

    @action(methods=['GET'], detail=False)
    def retrieve_unit(self, request):
        pass

    @action(methods=['POST'], detail=False)
    def update_unit(self, request):
        pass


class VideoViewSet(viewsets.ViewSet):

    @action(methods=['POST'], detail=False)
    def add_video(self, request):
        pass

    @action(methods=['GET'], detail=False)
    def list_videos(self, request):
        pass  # list unit videos

    @action(methods=['GET'], detail=False)
    def retrieve_video(self, request):
        pass

    @action(methods=['POST'], detail=False)
    def update_video(self, request):
        pass

    @action(methods=['POST'], detail=False)
    def delete_video(self, request):
        pass
