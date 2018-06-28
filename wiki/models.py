from django.db import models
import os
from django.conf import settings

# Create your models here.

class Page(models.Model):
    page_name = models.CharField(max_length=60, primary_key=True)
    page_content = models.TextField()
    page_counter = models.IntegerField(default=1)

    def inchits(self):
        self.page_counter += 1
        self.save()

    def __str__(self):
        return self.page_name

    def get_absolute_url(self):
        pass

class UserFile(models.Model):
    content = models.FileField(upload_to='uploads/')

    def __str__(self):
        return self.content.name

    def get_absolute_url(self):
        return self.content.url

    def delete(self, *args, **kwargs):
        dir = os.path.dirname(os.path.join(settings.MEDIA_ROOT, self.content.name))
        try:
            self.content.delete()
        except OSError:
            pass
        try:
            os.rmdir(dir)
        except OSError:
            pass
        return models.Model.delete(self)
        #print('Deleting {0}'.format(self.content.name))
        #super().delete(self)