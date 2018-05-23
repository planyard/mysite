from django.forms import ModelForm
from .models import UserFile

class FileUploadForm(ModelForm):
    class Meta:
        model = UserFile
        fields = '__all__'