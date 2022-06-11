from django import forms
from school import models as school_models


class AddVideoForm(forms.Form):
    form = forms.ModelChoiceField(queryset=school_models.FormModel.objects.all(), label="Form", required=True,
                                  widget=forms.Select(attrs={"class": "form-control "
                                                                      "shadow-none rounded-0 mb-2", "id": "_form"}))
    subject = forms.ModelChoiceField(queryset=school_models.SubjectModel.objects.all(), label="Subject", required=True,
                                     widget=forms.Select(attrs={"class": "form-control shadow-none "
                                                                         "rounded-0 mb-2", "id": "_subject"}))
    unit = forms.ChoiceField(label="Unit", required=True,
                             widget=forms.Select(attrs={"class": "form-control "
                                                                 "shadow-none rounded-0 mb-2", "id": "_unit"}))
    label = forms.CharField(label="Video Label", max_length=255, required=True,
                            widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    index = forms.IntegerField(label="Video Index",
                               widget=forms.NumberInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    video = forms.FileField(label="Video File", required=True,
                            widget=forms.FileInput(attrs={"class": "form-control shadow-none rounded-0"}))


class AddSubjectForm(forms.Form):
    name = forms.CharField(label="Name", label_suffix="", required=True,
                           widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    description = forms.CharField(label="Description", label_suffix="",
                                  widget=forms.Textarea(attrs={"class": "form-control shadow-none rounded-0"}))


class AddForm(forms.Form):
    name = forms.CharField(label="Name", label_suffix="", required=True,
                           widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))


class AddUnitForm(forms.Form):
    name = forms.CharField(label="Name", label_suffix="", required=True,
                           widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    form = forms.ModelChoiceField(queryset=school_models.FormModel.objects.all(), label="Form", required=True,
                                  widget=forms.Select(attrs={"class": "form-control "
                                                                      "shadow-none rounded-0 mb-2", "id": "_form"}))
    subject = forms.ModelChoiceField(queryset=school_models.SubjectModel.objects.all(), label="Subject", required=True,
                                     widget=forms.Select(attrs={"class": "form-control shadow-none "
                                                                         "rounded-0", "id": "_subject"}))
