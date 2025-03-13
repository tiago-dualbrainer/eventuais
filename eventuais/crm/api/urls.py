from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from eventuais.crm.views import AccountViewSet
from eventuais.crm.views import ActivityViewSet
from eventuais.crm.views import ContactViewSet
from eventuais.crm.views import ContentTypeViewSet
from eventuais.crm.views import CustomFieldValueViewSet
from eventuais.crm.views import CustomFieldViewSet
from eventuais.crm.views import OpportunityViewSet
from eventuais.crm.views import SocialProfileViewSet
from eventuais.crm.views import TagViewSet
from eventuais.crm.views_additional import CampaignRecipientViewSet
from eventuais.crm.views_additional import CampaignViewSet
from eventuais.crm.views_additional import DashboardItemViewSet
from eventuais.crm.views_additional import DashboardViewSet
from eventuais.crm.views_additional import MarketingEmailViewSet
from eventuais.crm.views_additional import ReportViewSet
from eventuais.crm.views_additional import SegmentViewSet
from eventuais.crm.views_additional import SupportTicketViewSet
from eventuais.crm.views_additional import TicketMessageViewSet

router = DefaultRouter()
router.register(r"tags", TagViewSet)
router.register(r"activities", ActivityViewSet)
router.register(r"custom-fields", CustomFieldViewSet)
router.register(r"custom-field-values", CustomFieldValueViewSet)
router.register(r"social-profiles", SocialProfileViewSet)
router.register(r"accounts", AccountViewSet)
router.register(r"contacts", ContactViewSet)
router.register(r"opportunities", OpportunityViewSet)
router.register(r"content-types", ContentTypeViewSet)
router.register(r"campaigns", CampaignViewSet)
router.register(r"marketing-emails", MarketingEmailViewSet)
router.register(r"campaign-recipients", CampaignRecipientViewSet)
router.register(r"segments", SegmentViewSet)
router.register(r"support-tickets", SupportTicketViewSet)
router.register(r"ticket-messages", TicketMessageViewSet)
router.register(r"reports", ReportViewSet)
router.register(r"dashboards", DashboardViewSet)
router.register(r"dashboard-items", DashboardItemViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
