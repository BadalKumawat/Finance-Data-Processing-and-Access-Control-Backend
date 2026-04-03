from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = request.user.role.upper() if request.user.role else ''
        return user_role == 'ADMIN'
    

# class IsAnalystRole(BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'ANALYST'])


class IsAdminOrSelf(BasePermission):

    # ADMIN Can do anything (List, Create, Update, Delete).
    # Normal user can only see and update only its profile and details

    
    def has_permission(self, request, view):
        # User must be logged in 
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = request.user.role.upper() if request.user.role else ''
        action = getattr(view, 'action', None)
        
        if action in ['list', 'create']:
            return user_role == 'ADMIN'
            
        return True

    def has_object_permission(self, request, view, obj):
        user_role = request.user.role.upper() if request.user.role else ''
        if user_role == 'ADMIN':
            return True
            
        if request.method in ['GET', 'PUT', 'PATCH']:
            return obj == request.user
            
        return False