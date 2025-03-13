from rest_framework import permissions


class IsProjectMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a project to access it.
    To be implemented with project membership model.
    """

    def has_object_permission(self, request, view, obj):
        # Write logic to check if user is a member of the project
        # For now, we'll just use IsAuthenticated
        return True
