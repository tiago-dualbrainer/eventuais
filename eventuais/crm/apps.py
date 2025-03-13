from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CrmConfig(AppConfig):
    name = "eventuais.crm"
    verbose_name = _("CRM")

