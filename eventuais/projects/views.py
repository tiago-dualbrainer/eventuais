from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import permissions
from rest_framework import viewsets

from .models import Comment
from .models import Crew
from .models import Equipment
from .models import Project
from .models import ProjectResourceAllocation
from .models import Task
from .models import Transportation
from .permissions import IsProjectMember
from .serializers import CommentSerializer
from .serializers import CrewSerializer
from .serializers import EquipmentSerializer
from .serializers import ProjectResourceAllocationSerializer
from .serializers import ProjectSerializer
from .serializers import TaskSerializer
from .serializers import TransportationSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "start_date", "end_date", "created_at"]


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "model_number", "category"]


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["role"]
    search_fields = ["name", "role", "skills"]


class TransportationViewSet(viewsets.ModelViewSet):
    queryset = Transportation.objects.all()
    serializer_class = TransportationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["vehicle_type"]
    search_fields = ["name", "vehicle_type"]


class ProjectResourceAllocationViewSet(viewsets.ModelViewSet):
    queryset = ProjectResourceAllocation.objects.all()
    serializer_class = ProjectResourceAllocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["project"]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["project", "assignee", "status", "priority"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "priority", "status"]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["task", "author"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
