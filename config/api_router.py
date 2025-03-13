from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from eventuais.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

# Add routes to the API router here
# Don't add more ViewSets directly here; include app-specific URL configurations instead

app_name = "api"
urlpatterns = router.urls

# Include CRM API URLs
urlpatterns += [
    path("crm/", include("eventuais.crm.api.urls")),
]
