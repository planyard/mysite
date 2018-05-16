from django.db import models

# Create your models here.

class Page(models.Model):
    page_name = models.CharField(max_length=60, primary_key=True)
    page_content = models.TextField()

    def __str__(self):
        return self.page_name

    def get_absolute_url(self):
        pass