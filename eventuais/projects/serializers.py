from rest_framework import serializers
from .models import Project, Equipment, Crew, Transportation, ProjectResourceAllocation, Task, Comment


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Project
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Equipment
        fields = "__all__"
        read_only_fields = ("id", "type", "created_at", "updated_at")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Crew
        fields = "__all__"
        read_only_fields = ("id", "type", "created_at", "updated_at")


class TransportationSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Transportation
        fields = "__all__"
        read_only_fields = ("id", "type", "created_at", "updated_at")


class ProjectResourceAllocationSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = ProjectResourceAllocation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, data):
        """
        Validate that only one resource type is provided and check for overlapping allocations.
        """
        # Check that only one resource type is provided
        resource_fields = ["equipment", "crew", "transportation"]
        resource_count = sum(1 for field in resource_fields if data.get(field) is not None)

        if resource_count == 0:
            raise serializers.ValidationError("At least one resource must be provided.")

        if resource_count > 1:
            raise serializers.ValidationError("Only one resource type can be allocated at a time.")

        # Check for overlapping allocations
        start = data.get("allocation_start")
        end = data.get("allocation_end")

        if start >= end:
            raise serializers.ValidationError("End time must be after start time.")

        # Determine which resource is being allocated
        resource = None
        resource_type = None

        if data.get("equipment"):
            resource = data.get("equipment")
            resource_type = "equipment"
        elif data.get("crew"):
            resource = data.get("crew")
            resource_type = "crew"
        elif data.get("transportation"):
            resource = data.get("transportation")
            resource_type = "transportation"

        # Check for overlapping allocations for the same resource
        existing_allocations = ProjectResourceAllocation.objects.filter(**{resource_type: resource})

        # Exclude current instance in case of update
        if self.instance:
            existing_allocations = existing_allocations.exclude(id=self.instance.id)

        for allocation in existing_allocations:
            if start < allocation.allocation_end and end > allocation.allocation_start:
                raise serializers.ValidationError(
                    f"This resource is already allocated during the requested time period."
                )

        return data


class TaskSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Task
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:  # type: ignore
        model = Comment
        fields = "__all__"
        read_only_fields = ("id", "author", "created_at", "updated_at")

    def get_author_name(self, obj):
        return obj.author.name if obj.author else None

    def create(self, validated_data):
        # Set the author to the current user
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
