from django.contrib import admin

from .models import SAMLSetting


@admin.register(SAMLSetting)
class SAMLSettingAdmin(admin.ModelAdmin):
    pass
