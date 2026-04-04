from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import FilteredRelation, Q, F, Count
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache

from pinterest.forms import PinCreateModelForm, PinUpdateModelForm, CommentForm
from pinterest.models import Pin, SavedPin, Board, Like, Comment
from pinterest.permissions import IsBoardOwnerMixin, IsPinOwnerMixin


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class PinCreateView(generic.CreateView):
    model = Pin
    form_class = PinCreateModelForm
    template_name = 'pinterest/create_pin.html'
    success_url = '/'

    def get_form(self, form_class=None):
        form = super(PinCreateView, self).get_form(form_class)
        form.instance.user = self.request.user
        if self.kwargs.get('input_value') == 'idea_pin':
            form.instance.is_idea = True
        return form


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class PinUpdateView(generic.UpdateView):
    model = Pin
    form_class = PinUpdateModelForm
    template_name = 'pinterest/edit_pin.html'
    slug_url_kwarg = 'id'
    slug_field = 'id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().user != request.user:
            raise PermissionDenied("You are not the owner of this pin")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('pins:detail_pin', kwargs={'id': self.object.id})


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class PinDeleteView(generic.DeleteView):
    model = Pin
    template_name = 'pinterest/confirm_delete_pin.html'
    slug_url_kwarg = 'id'
    slug_field = 'id'
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().user != request.user:
            raise PermissionDenied("You are not the owner of this pin")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class PinDetailView(IsPinOwnerMixin, generic.DetailView):
    model = Pin
    template_name = 'pinterest/detail_pin.html'
    slug_url_kwarg = 'id'
    slug_field = 'id'
    context_object_name = 'pin_obj'

    def get_context_data(self, **kwargs):
        context = super(PinDetailView, self).get_context_data(**kwargs)
        pin = context['pin_obj']
        user_id = self.request.user.id

        # Suggested pins
        context['suggested_pins'] = self.model.objects.filter(
            category__name__in=list(pin.category.values_list('name', flat=True))
        ).annotate(
            is_saved_pin=FilteredRelation('saved_pins', condition=Q(saved_pins__user_id=user_id)),
            is_liked_pin=FilteredRelation('likes', condition=Q(likes__user_id=user_id))
        ).annotate(
            is_saved=F('is_saved_pin'), is_liked=F('is_liked_pin'),
            like_count=Count('likes', distinct=True)
        ).distinct().exclude(id=pin.id)

        # Likes
        context['like_count'] = pin.likes.count()
        context['is_liked'] = pin.likes.filter(user_id=user_id).exists()

        # Comments (top-level with replies prefetched)
        context['comments'] = pin.comments.filter(parent__isnull=True).select_related(
            'user', 'user__user_profile'
        ).prefetch_related('replies__user', 'replies__user__user_profile')
        context['comment_form'] = CommentForm()

        # Boards
        context['boards'] = self.request.user.boards.all()
        return context


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class SaveUnsavePin(generic.View):
    def get(self, request, pin_id):
        saved_obj = SavedPin.objects.filter(pin_id=pin_id, user=request.user)
        if saved_obj:
            saved_obj.delete()
        else:
            SavedPin.objects.create(pin_id=pin_id, user=request.user)
        return redirect(request.META['HTTP_REFERER'])


class SearchPinByCategoryListView(generic.View):
    template_name = 'pinterest/search_pin_category.html'

    def get(self, request):
        data = self.get_queryset()
        context = {'data': data}
        return render(request=request, template_name=self.template_name, context=context)

    def search_filters(self):
        search_param = self.request.GET.get('search_input')
        if not search_param:
            search_param = ','
        else:
            search_param = search_param.title()
        search_query = Q(category__name=search_param)
        return search_query

    def get_queryset(self):
        if self.request.user.is_authenticated:
            filter_params = self.search_filters() & (Q(is_private=False) | Q(user=self.request.user))
        else:
            filter_params = self.search_filters() & Q(is_private=False)
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        return Pin.objects.filter(filter_params).annotate(
            is_saved_pin=FilteredRelation('saved_pins', condition=Q(saved_pins__user_id=user_id))
        ).annotate(is_saved=F('is_saved_pin')).distinct()[:20]


class PinAddToBoard(generic.View):
    def get(self, request, board_id, pin_id):
        board_obj = Board.objects.filter(id=board_id)
        if board_obj:
            if not board_obj.first().pin.filter(id=pin_id):
                board_obj.first().pin.add(pin_id)
        return redirect(request.META['HTTP_REFERER'])


class DeleteBoard(IsBoardOwnerMixin, generic.View):
    def get(self, request, board_id):
        board_obj = self.get_object()
        if board_obj:
            board_obj.delete()
        return redirect(request.META['HTTP_REFERER'])

    def get_object(self):
        board_id = self.kwargs.get('board_id')
        board_obj = Board.objects.filter(id=board_id).first()
        if board_obj:
            return board_obj
        return None


class MakePublicPrivateBoard(IsBoardOwnerMixin, generic.View):
    def get(self, request, board_id):
        board_obj = self.get_object()
        if board_obj.is_private:
            board_obj.is_private = False
        else:
            board_obj.is_private = True
        board_obj.save()
        return redirect(request.META['HTTP_REFERER'])

    def get_object(self):
        board_obj = Board.objects.filter(id=self.kwargs.get('board_id')).first()
        if board_obj:
            return board_obj
        else:
            return None


class RemovePinFromBoard(IsBoardOwnerMixin, generic.View):
    def get(self, request, board_id, pin_id):
        board_obj = self.get_object()
        if board_obj and pin_id in board_obj.pin.values_list('id', flat=True):
            board_obj.pin.remove(pin_id)
        return redirect(request.META['HTTP_REFERER'])

    def get_object(self):
        board_obj = Board.objects.filter(id=self.kwargs.get('board_id')).first()
        if board_obj:
            return board_obj
        else:
            return None


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class LikeUnlikePin(generic.View):
    def get(self, request, pin_id):
        like_obj = Like.objects.filter(pin_id=pin_id, user=request.user)
        if like_obj:
            like_obj.delete()
        else:
            Like.objects.create(pin_id=pin_id, user=request.user)
        return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class AddComment(generic.View):
    def post(self, request, pin_id):
        text = request.POST.get('text', '').strip()
        parent_id = request.POST.get('parent_id')
        if text:
            comment = Comment(pin_id=pin_id, user=request.user, text=text)
            if parent_id:
                comment.parent_id = parent_id
            comment.save()
        return redirect('pins:detail_pin', id=pin_id)


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class DeleteComment(generic.View):
    def get(self, request, comment_id):
        comment = Comment.objects.filter(id=comment_id, user=request.user).first()
        if comment:
            pin_id = comment.pin_id
            comment.delete()
            return redirect('pins:detail_pin', id=pin_id)
        return redirect(request.META.get('HTTP_REFERER', '/'))


def error_404(request, exception):
    return render(request=request, template_name='404.html', status=404)


def error_400(request, exception):
    return render(request=request, template_name='400.html', status=400)


def error_403(request, exception):
    return render(request=request, template_name='403.html', status=403)


def error_500(request):
    return render(request=request, template_name='500.html', status=500)
