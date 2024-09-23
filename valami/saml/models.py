from django.db import models


class SAMLSetting(models.Model):
    settings = models.JSONField()
    advanced_settings = models.JSONField()
