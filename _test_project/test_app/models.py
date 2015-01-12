from django.db import models


class TestModel(models.Model):
    char = models.CharField(max_length=255, null=True)
    text = models.TextField(null=True)
    datetime = models.DateTimeField(null=True)