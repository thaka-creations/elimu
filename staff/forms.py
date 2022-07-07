from django import forms
from school import models as school_models


class AddVideoForm(forms.Form):
    form = forms.ModelChoiceField(queryset=school_models.FormModel.objects.all(), label="Form", required=True,
                                  widget=forms.Select(attrs={"class": "form-control "
                                                                      "shadow-none rounded-0 mb-2", "id": "a_form"}))
    subject = forms.ModelChoiceField(queryset=school_models.SubjectModel.objects.all(), label="Subject", required=True,
                                     widget=forms.Select(attrs={"class": "form-control shadow-none "
                                                                         "rounded-0 mb-2", "id": "a_subject"}))
    unit = forms.ChoiceField(label="Unit", required=True,
                             widget=forms.Select(attrs={"class": "form-control "
                                                                 "shadow-none rounded-0 mb-2", "id": "a_unit"}))
    label = forms.CharField(label="Video Label", max_length=255, required=True,
                            widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    index = forms.IntegerField(label="Video Index",
                               widget=forms.NumberInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))


class CoverVideoForm(forms.Form):
    label = forms.CharField(label="Video Label", max_length=255, required=True,
                            widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    video = forms.FileField(label="Video File", required=True,
                            widget=forms.FileInput(attrs={"class": "form-control shadow-none rounded-0"}))


class AddSubjectForm(forms.Form):
    name = forms.CharField(label="Name", label_suffix="", required=True,
                           widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))


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


class AddCountyForm(forms.Form):
    name = forms.CharField(label="Name", label_suffix="", required=True,
                           widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))


ALLOWED_PERIOD = [
    ("DAY", "DAY"),
    ("DAYS", "DAYS"),
    ("MONTH", "MONTH"),
    ("MONTHS", "MONTHS"),
    ("YEAR", "YEAR"),
    ("YEARS", "YEARS")
]


class AddUnitAmount(forms.Form):
    unit = forms.ModelChoiceField(queryset=school_models.UnitModel.objects.all(), label="Unit", required=True,
                                  widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    amount = forms.IntegerField(label="Amount",
                                widget=forms.NumberInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    period = forms.IntegerField(label="Period",
                                widget=forms.NumberInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    period_type = forms.ChoiceField(label="Period Type", choices=ALLOWED_PERIOD,
                                    widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))


class AddSubjectAmount(forms.Form):
    subject = forms.ModelChoiceField(queryset=school_models.SubjectModel.objects.all(), label="Subject", required=True,
                                     widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    form = forms.ModelChoiceField(queryset=school_models.FormModel.objects.all(), label="Form", required=True,
                                  widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    amount = forms.IntegerField(label="Amount",
                                widget=forms.NumberInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    period = forms.IntegerField(label="Period",
                                widget=forms.NumberInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    period_type = forms.ChoiceField(label="Period Type", choices=ALLOWED_PERIOD,
                                    widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))


class AddFormAmount(forms.Form):
    form = forms.ModelChoiceField(queryset=school_models.FormModel.objects.all(), label="Form", required=True,
                                  widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    amount = forms.IntegerField(label="Amount",
                                widget=forms.NumberInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    period = forms.IntegerField(label="Period",
                                widget=forms.NumberInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    period_type = forms.ChoiceField(label="Period Type", choices=ALLOWED_PERIOD,
                                    widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))


class AddAgent(forms.Form):
    name = forms.CharField(label="Name", label_suffix="", required=True,
                           widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    email = forms.EmailField(label="Email", label_suffix="", required=True,
                             widget=forms.EmailInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
    code = forms.CharField(label="User Code", label_suffix="", required=True,
                           widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0 mb-2"}))
