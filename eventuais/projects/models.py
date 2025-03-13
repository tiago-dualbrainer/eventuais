import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from eventuais.users.models import User


class Project(models.Model):
    """Project model for managing event projects."""

    class Status(models.TextChoices):
        PLANNED = "planned", _("Planned")
        IN_PROGRESS = "in_progress", _("In Progress")
        COMPLETED = "completed", _("Completed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Project Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.PLANNED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    """Abstract base class for all types of resources."""

    class ResourceType(models.TextChoices):
        EQUIPMENT = "equipment", _("Equipment")
        CREW = "crew", _("Crew")
        TRANSPORTATION = "transportation", _("Transportation")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Resource Name"), max_length=255)
    type = models.CharField(_("Resource Type"), max_length=20, choices=ResourceType.choices)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore
        abstract = True

    def __str__(self):
        return f"{self.name} ({self.type})"


class Equipment(Resource):
    """Equipment resource model."""

    model_number = models.CharField(_("Model Number"), max_length=100, blank=True)
    category = models.CharField(_("Category"), max_length=100)

    def save(self, *args, **kwargs):
        self.type = Resource.ResourceType.EQUIPMENT
        super().save(*args, **kwargs)


class Crew(Resource):
    """Crew resource model."""

    role = models.CharField(_("Role"), max_length=100)
    skills = models.TextField(_("Skills"), blank=True)

    def save(self, *args, **kwargs):
        self.type = Resource.ResourceType.CREW
        super().save(*args, **kwargs)


class Transportation(Resource):
    """Transportation resource model."""

    vehicle_type = models.CharField(_("Vehicle Type"), max_length=100)
    capacity = models.PositiveIntegerField(_("Capacity"))

    def save(self, *args, **kwargs):
        self.type = Resource.ResourceType.TRANSPORTATION
        super().save(*args, **kwargs)


class ProjectResourceAllocation(models.Model):
    """Model for allocating resources to projects."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="resource_allocations")
    # Using generic foreign key pattern for different resource types
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True)
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, null=True, blank=True)
    transportation = models.ForeignKey(Transportation, on_delete=models.CASCADE, null=True, blank=True)
    allocation_start = models.DateTimeField(_("Allocation Start"))
    allocation_end = models.DateTimeField(_("Allocation End"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        resource = self.equipment or self.crew or self.transportation
        return f"{self.project.name} - {resource.name if resource else 'Unknown'}"


class Task(models.Model):
    """Task model for project management."""

    class Status(models.TextChoices):
        TO_DO = "to_do", _("To Do")
        IN_PROGRESS = "in_progress", _("In Progress")
        DONE = "done", _("Done")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.TO_DO)
    priority = models.CharField(_("Priority"), max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comment model for tasks."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(_("Content"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.name} on {self.task.title}"
