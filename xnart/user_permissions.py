from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

class IsVerifiedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if the user is verified
        if not request.user.is_verified:
            message = {'message': 'You are not verified' }  # Customize the message here
            raise PermissionDenied(detail=message)
        
        return True
