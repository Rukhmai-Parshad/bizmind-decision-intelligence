from django import forms
from .models import Dataset


class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'type', 'file']

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        type = cleaned_data.get('type')

        if file and type:
            if Dataset.objects.filter(file=file, type=type).exists():
                raise forms.ValidationError(
                    "This dataset file has already been uploaded for this type."
                )

        return cleaned_data
