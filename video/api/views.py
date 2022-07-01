import requests
import json
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from video.api import serializers as video_serializers


class GetVideoOtp(APIView):
    def get(self, request):
        serializer = video_serializers.GetVideoOtpSerializer(data=request.query_params.dict(), many=False)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        video_id = validated_data['video_id']

        url = "https://dev.vdocipher.com/api/videos/{}/otp".format(video_id)
        payload = json.dumps({"ttl": False})
        headers = {
            "Authorization": "Apisecret " + settings.VDOCIPHER_SECRET,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(url, data=payload, headers=headers)
        return Response(json.loads(response.text), status=status.HTTP_200_OK)


class Video(APIView):
    def post(self, request):
        # url = "https://dev.vdocipher.com/api/videos"
        # headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}
        # querystring = {"title": "cover"}
        # resp = requests.request("PUT", url, headers=headers, params=querystring)
        # print("testing")
        # print(resp)
        return Response("one")
