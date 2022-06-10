from rest_framework import serializers


class GetVideoOtpSerializer(serializers.Serializer):
    video_id = serializers.CharField(required=True)
