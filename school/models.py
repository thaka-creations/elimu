import uuid
from django.db import models


# Create your models here.
class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class FormModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class SubjectModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class TopicModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(SubjectModel, on_delete=models.CASCADE, related_name="form_topics")
    form = models.ForeignKey(FormModel, on_delete=models.CASCADE, related_name="subject_topics")
    index = models.BigIntegerField(default=0)

    class Meta:
        ordering = ['index']

    def __str__(self):
        return self.name


class UnitModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    topic = models.ForeignKey(TopicModel, on_delete=models.CASCADE, related_name="topic_units", null=True)
    index = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['index']


class VideoModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey(UnitModel, on_delete=models.CASCADE, related_name="videos", blank=True, null=True)
    videoid = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.videoid


class CoverVideo(BaseModel):
    label = models.CharField(max_length=255, blank=True, null=True)
    videoid = models.CharField(max_length=255, blank=True, null=True)
