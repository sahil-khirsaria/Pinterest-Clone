from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


class IsBoardOwnerMixin(object):
    permission_denied_message = _("You are not the owner of this board - you cannot edit or view it")

    def dispatch(self, request, *args, **kwargs):
        if self.get_object() and self.get_object().user != request.user:
            raise PermissionDenied(self.get_permission_denied_message())
        return super().dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message


class PrivateBoardViewMixin(object):
    permission_denied_message = _("You are not the owner of this board - you cannot edit or view it")

    def dispatch(self, request, *args, **kwargs):
        board_obj = self.get_object()
        if board_obj and board_obj.is_private and board_obj.user != request.user:
            raise PermissionDenied(self.get_permission_denied_message())
        return super().dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message


class IsPinOwnerMixin(object):
    permission_denied_message = _("You are not the owner of this pin - you cannot edit or view it")

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_private and self.get_object().user != request.user:
            raise PermissionDenied(self.get_permission_denied_message())
        return super().dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message


