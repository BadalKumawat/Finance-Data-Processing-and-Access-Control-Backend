from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerAdminOrAnalyst(BasePermission):
    """
        ADMIN: Full access to everything
        ANALYST: Read-only access 
        NORMAL USER: Can only perform CRUD on their OWN accounts and transactions.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.role == 'VIEWER':
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user_role = request.user.role.upper()

        if user_role == 'ADMIN':
            return True
        if user_role == 'ANALYST' and request.method in SAFE_METHODS:
            return True
        
        # Check if the user is the owner of the object (Account or Transaction)
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        return False