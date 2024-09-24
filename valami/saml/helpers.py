from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser

from .models import SAMLSetting


def get_saml_settings():
    try:
        return SAMLSetting.objects.get()
    except SAMLSetting.DoesNotExist:
        return None


def set_saml_settings(settings, advanced_settings):
    current_settings_obj = SAMLSetting.objects.first()
    current_settings = getattr(current_settings_obj, "settings", {}) or {}
    current_advanced_settings = (
        getattr(current_settings_obj, "advanced_settings", {}) or {}
    )

    merged_settings = {**current_settings, **settings}
    merged_advanced_settings = {**current_advanced_settings, **advanced_settings}

    SAMLSetting.objects.update_or_create(
        defaults={
            "settings": merged_settings,
            "advanced_settings": merged_advanced_settings,
        }
    )


def set_idp_metadata(metadata_xml: str):
    idp_metadata = OneLogin_Saml2_IdPMetadataParser.parse(metadata_xml)

    current_settings = get_saml_settings()
    new_settings = OneLogin_Saml2_IdPMetadataParser.merge_settings(
        current_settings.settings, idp_metadata
    )

    set_saml_settings(new_settings, current_settings.advanced_settings)
