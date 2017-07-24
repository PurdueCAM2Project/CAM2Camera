from rest_framework import permissions, exceptions

class CAM2Permission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method.lower() == 'get':
            return request.user
        if request.method.lower() == 'post':
            return self.only_admin(request)
        if request.method.lower() == 'patch':
            return self.only_admin(request)
        if request.method.lower() == 'delete':
            return self.only_admin(request)

    def only_admin(self, request):
        if request.user:
            try:
                permission_level = request.user.permission_level
            except AttributeError:
                return False
            return permission_level == 'Admin'
        else:
            return False        
