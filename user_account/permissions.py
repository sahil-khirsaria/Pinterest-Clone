from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


class IsOwnerMixin(object):
    permission_denied_message = _("You are not the owner of this profile - you cannot edit it")

    def dispatch(self, request, *args, **kwargs):
        if self.get_object() != request.user:
            raise PermissionDenied(self.get_permission_denied_message())
        return super().dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message
