from django.contrib import admin
from django.urls import path

from .views import Metadata, SAMLView, UploadIDPMetadata

admin.autodiscover()

urlpatterns = [
    path("", SAMLView.as_view(), name="saml_view"),
    path("metadata", Metadata.as_view(), name="metadata_view"),
    path(
        "upload-idp-metadata",
        UploadIDPMetadata.as_view(),
        name="upload_idp_metadata_view",
    ),
]
