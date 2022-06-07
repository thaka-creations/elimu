import requests
from django.conf import settings
from requests_toolbelt import MultipartEncoder
from django.core.files.storage import FileSystemStorage


def upload_video(filepath, video_name, instance):
    url = "https://dev.vdocipher.com/api/videos"
    headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}
    querystring = {"title": video_name}
    resp = requests.request("PUT", url, headers=headers, params=querystring)

    if resp.status_code == 403:
        return

    upload_info = resp.json()
    client_payload = upload_info['clientPayload']
    upload_link = client_payload['uploadLink']
    instance.videoid = upload_info['videoId']
    instance.save()

    print(instance)

    m = MultipartEncoder(fields=[
        ('x-amz-credential', client_payload['x-amz-credential']),
        ('x-amz-algorithm', client_payload['x-amz-algorithm']),
        ('x-amz-date', client_payload['x-amz-date']),
        ('x-amz-signature', client_payload['x-amz-signature']),
        ('key', client_payload['key']),
        ('policy', client_payload['policy']),
        ('success_action_status', '201'),
        ('success_action_redirect', ''),
        ('file', ('filename', open(filepath, 'rb'), 'text/plain'))
    ])

    requests.post(
        upload_link,
        data=m,
        headers={'Content-Type': m.content_type}
    )

    fs = FileSystemStorage()
    fs.delete(video_name)
