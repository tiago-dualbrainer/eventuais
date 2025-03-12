from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet
from .views import CrewViewSet
from .views import EquipmentViewSet
from .views import ProjectResourceAllocationViewSet
from .views import ProjectViewSet
from .views import TaskViewSet
from .views import TransportationViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"equipment", EquipmentViewSet)
router.register(r"crew", CrewViewSet)
router.register(r"transportation", TransportationViewSet)
router.register(r"allocations", ProjectResourceAllocationViewSet)
router.register(r"tasks", TaskViewSet)
router.register(r"comments", CommentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
