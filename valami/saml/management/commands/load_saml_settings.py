import copy

from django.core.management.base import BaseCommand
from django_tenants.utils import get_tenant_model, tenant_context

from valami.saml.default_settings import advanced_settings, settings
from valami.saml.helpers import set_saml_settings


class Command(BaseCommand):
    help = "Loads default SAML metadata into tenants"

    def handle(self, *args, **options):
        for tenant in get_tenant_model().objects.all():
            with tenant_context(tenant):
                domain = tenant.get_primary_domain()
                new_settings = copy.deepcopy(settings)
                sp_settings = new_settings["sp"]
                acs_service = sp_settings["assertionConsumerService"]
                sls_service = sp_settings["singleLogoutService"]
                acs_service["url"] = acs_service["url"].format(domain=domain)
                sls_service["url"] = sls_service["url"].format(domain=domain)

                print(new_settings)

                set_saml_settings(new_settings, advanced_settings)

        self.stdout.write(self.style.SUCCESS("Successfully closed poll "))
