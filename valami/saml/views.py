import base64
import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from valami.users.serializers import PublicUserSerializer

from .helpers import get_saml_settings, set_idp_metadata

logger = logging.getLogger(__name__)
User = get_user_model()


class SAMLView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        request_data = self.prepare_django_request(request=request)
        self.auth = self.init_saml_auth(request_data)

        if "sso" in request.GET:
            return self.handle_sso()
        elif "slo" in request.GET:
            return self.handle_slo(request)
        elif "sls" in request.GET:
            return self.handle_sls(request)

    def post(self, request, *args, **kwargs):
        request_data = self.prepare_django_request(request=request)
        self.auth = self.init_saml_auth(request_data)

        if "acs" in request.GET:
            return self.handle_acs(request)

    def handle_sso(self):
        return HttpResponseRedirect(self.auth.login())

    def handle_slo(self, request):
        name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
        if "samlNameId" in request.session:
            name_id = request.session["samlNameId"]
        if "samlSessionIndex" in request.session:
            session_index = request.session["samlSessionIndex"]
        if "samlNameIdFormat" in request.session:
            name_id_format = request.session["samlNameIdFormat"]
        if "samlNameIdNameQualifier" in request.session:
            name_id_nq = request.session["samlNameIdNameQualifier"]
        if "samlNameIdSPNameQualifier" in request.session:
            name_id_spnq = request.session["samlNameIdSPNameQualifier"]
        logout(request)
        return HttpResponseRedirect(
            self.auth.logout(
                name_id=name_id,
                session_index=session_index,
                nq=name_id_nq,
                name_id_format=name_id_format,
                spnq=name_id_spnq,
            ),
        )

    def handle_sls(self, request):
        request_id = None
        if "LogoutRequestID" in request.session:
            request_id = request.session["LogoutRequestID"]

        def delete_session_callback():
            request.session.flush()

        url = self.auth.process_slo(
            request_id=request_id, delete_session_cb=delete_session_callback
        )
        return HttpResponseRedirect(url)

    def handle_acs(self, request):
        self.auth.process_response()
        errors = self.auth.get_errors()

        if errors:
            logger.error(f"SAML authentication errors: {errors}")
            logger.error(self.auth.get_last_error_reason())

        if not self.auth.is_authenticated():
            return Response(f"SAML authentication failed. Errors: {errors}")

        attributes = self.auth.get_attributes()
        email = attributes.get("email", [""])[0]
        username = attributes.get("username", [""])[0]

        response = redirect(settings.SAML_LOGIN_REDIRECT_URL)

        print(email, username, attributes)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            if username and email:
                user = User.objects.create(
                    username=username,
                    email=email,
                    is_active=True,
                )
            else:
                return response
        finally:
            user_serializer = PublicUserSerializer(user)
            user_base64 = base64.b64encode(
                json.dumps(user_serializer.data).encode()
            ).decode()
            refresh_token = RefreshToken.for_user(user)

            response.set_cookie(
                "user", user_base64, httponly=False, secure=True, samesite="None"
            )
            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
            )

        return response

    @staticmethod
    def prepare_django_request(request):
        return {
            "https": "on" if request.is_secure() else "off",
            "http_host": request.META["HTTP_HOST"],
            "script_name": request.META["PATH_INFO"],
            "get_data": request.GET.copy(),
            # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
            # 'lowercase_urlencoding': True,
            "post_data": request.POST.copy(),
        }

    @staticmethod
    def init_saml_auth(request_data: dict):
        saml_settings = get_saml_settings()
        onelogin_saml_settings = OneLogin_Saml2_Settings(
            {
                **saml_settings.settings,
                **saml_settings.advanced_settings,
            },
        )
        return OneLogin_Saml2_Auth(request_data, onelogin_saml_settings)


class Metadata(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        saml_settings_obj = get_saml_settings()
        saml_settings = OneLogin_Saml2_Settings(
            {
                **saml_settings_obj.settings,
                **saml_settings_obj.advanced_settings,
            },
            sp_validation_only=True,
        )
        metadata = saml_settings.get_sp_metadata()
        errors = saml_settings.validate_metadata(metadata)

        if errors:
            print(errors)
            return HttpResponse(
                content=", ".join(errors), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return HttpResponse(content=metadata, content_type="text/xml")


class UploadIDPMetadata(APIView):
    def post(self, request):
        metadata_file = request.FILES.get("metadata")

        try:
            metadata = metadata_file.read()
            set_idp_metadata(metadata)
            return Response({"message": "Metadata was uploaded successfully."})
        except Exception:
            return Response(
                {
                    "error": "Something went wrong. Failed to upload IDP metadata.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
