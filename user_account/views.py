import datetime

from django.contrib.auth import get_user_model, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView, PasswordResetView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.db.models import Q, FilteredRelation, F
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import generic
from django.views.decorators.cache import never_cache

from pinterest.models import Pin, Board
from pinterest.permissions import PrivateBoardViewMixin
from user_account.forms import UserRegisterForm, UserUpdateForm, UserDetailUpdateForm, UserPasswordResetForm
from user_account.models import UserProfile
from user_account.permissions import IsOwnerMixin
from user_account.tokens import account_activation_token

User = get_user_model()


class HomePage(generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context['pins_objs'] = self.get_queryset()
        context['boards'] = self.get_boards()
        return context

    def search_filters(self):
        search_filter = Q()
        if self.request.user.is_authenticated:
            search_filter = Q(user=self.request.user) | Q(is_private=False) & \
                            Q(category__name__in=self.request.user.interest.values_list('name', flat=True))
        return search_filter

    def get_queryset(self):
        return Pin.objects.filter(self.search_filters()).annotate(
            is_saved_pin=FilteredRelation('saved_pins', condition=Q(saved_pins__user_id=self.request.user.id))
        ).annotate(is_saved=F('is_saved_pin')).distinct()[:20]

    def get_boards(self):
        if self.request.user.is_authenticated:
            return self.request.user.boards.all()
        return None


class TodayPinsView(generic.TemplateView):
    template_name = 'today.html'

    def get_context_data(self, **kwargs):
        context = super(TodayPinsView, self).get_context_data(**kwargs)
        today = datetime.date.today()
        if self.kwargs.get('category_name') == 'category':
            context['categories'] = Pin.objects.filter(created_at__date=today).values_list(
                'category__name', flat=True).distinct()[:15]
        else:
            filters = Q(created_at__date=today, category__name=self.kwargs.get('category_name'))
            if self.request.user.is_authenticated:
                filters = filters & (Q(is_private=False) | Q(user=self.request.user))
                context['pins_objs'] = Pin.objects.filter(filters).annotate(
                    is_saved_pin=FilteredRelation('saved_pins', condition=Q(saved_pins__user_id=self.request.user.id))
                ).annotate(is_saved=F('is_saved_pin')).distinct().order_by('-created_at')
            else:
                context['pins_objs'] = Pin.objects.filter(filters)
        return context


class UserRegisterView(generic.CreateView):
    form_class = UserRegisterForm
    model = User
    template_name = 'user_account/registration.html'
    success_url = reverse_lazy("home")

    def get_form(self, form_class=None):
        form = super(UserRegisterView, self).get_form(form_class=form_class)
        form.request = self.request
        return form


class UserEmailVerification(generic.View):
    def get(self, request, uid, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect(to='home')
        else:
            return render(request=request, template_name='', context={})


class UserPasswordResetView(PasswordResetView):
    template_name = 'user_account/password_reset.html'
    email_template_name = 'emails/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    form_class = UserPasswordResetForm

    def get_form(self, form_class=None):
        form = super(UserPasswordResetView, self).get_form(form_class=form_class)
        form.request = self.request
        return form


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'user_account/password_reset_done.html'


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'user_account/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'user_account/password_reset_complete.html'


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class UserUpdateView(IsOwnerMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    profile_form = UserDetailUpdateForm
    change_password_form = PasswordChangeForm
    template_name = 'user_account/edit_user.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['change_password_form'] = self.change_password_form
        try:
            context['profile_form'] = self.profile_form(instance=self.request.user.user_profile)
        except Exception as e:
            context['profile_form'] = self.profile_form()
        return context

    def post(self, request, *args, **kwargs):
        user_profile_obj, created = UserProfile.objects.get_or_create(user=request.user)
        profile_form = self.profile_form(self.request.POST, instance=user_profile_obj)
        if profile_form.is_valid():
            profile_form.save()
        return super(UserUpdateView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('users:edit_user', kwargs={'username': self.request.user.username})


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class UserPasswordChangeView(IsOwnerMixin, PasswordChangeView):
    template_name = 'user_account/change_password.html'

    def get_form(self, form_class=None):
        form = super().get_form()
        form.fields.get('old_password').widget.attrs["class"] = 'form-control'
        form.fields.get('new_password1').widget.attrs["class"] = 'form-control'
        form.fields.get('new_password2').widget.attrs["class"] = 'form-control'
        return form

    def get_success_url(self):
        return reverse('users:user_profile', kwargs={'id': self.request.user.id})

    def get_object(self):
        return self.request.user


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class UserProfileView(generic.DetailView):
    model = User
    template_name = 'user_account/profile.html'
    slug_url_kwarg = 'id'
    slug_field = 'id'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        if self.request.user == context['user_obj']:
            context['created_pins'] = context['user_obj'].pins.annotate(
                is_saved_pin=FilteredRelation('saved_pins', condition=Q(saved_pins__user_id=self.request.user.id))
            ).annotate(is_saved=F('is_saved_pin')).distinct()[:20]
            context['boards'] = context['user_obj'].boards.all()
        else:
            context['created_pins'] = context['user_obj'].pins.filter(is_private=False).annotate(
                is_saved_pin=FilteredRelation('saved_pins', condition=Q(saved_pins__user_id=self.request.user.id))
            ).annotate(is_saved=F('is_saved_pin')).distinct()[:20]
            context['boards'] = context['user_obj'].boards.filter(is_private=False)
        context['user_boards'] = self.request.user.boards.all()
        context['saved_pins'] = context['user_obj'].saved_pins.annotate(
            is_saved_pin=FilteredRelation('pin__saved_pins', condition=Q(pin__saved_pins__user_id=self.request.user.id))
        ).annotate(is_saved=F('is_saved_pin')).distinct()[:20]
        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        board_obj = Board.objects.filter(name=name, user=request.user)
        if board_obj:
            return redirect(request.META['HTTP_REFERER'])
        is_private = request.POST.get('is_private')
        is_private = True if is_private in ['on', 'On', 'ON'] else False
        Board.objects.create(name=name, user=request.user, is_private=is_private)
        return redirect(request.META['HTTP_REFERER'])


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class UserDeleteView(IsOwnerMixin, generic.View):
    template_name = 'user_account/delete_user.html'

    def get(self, request, username):
        user_obj = User.objects.get(username=username, is_active=True)
        return render(request=request, template_name=self.template_name, context={'user_obj': user_obj})

    def post(self, request, username):
        user = User.objects.get(username=username, is_active=True)
        user.is_active = False
        user.save()
        logout(request)
        return redirect('login')

    def get_object(self):
        username = self.kwargs.get('username')
        return User.objects.get(username=username)


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class UserSearchView(generic.View):
    def get(self, request):
        search_params = self.search_filters()
        data = list(User.objects.filter(search_params).exclude(id=request.user.id))
        context = {'data': data}
        return render(request=request, template_name='user_account/user_search_page.html', context=context)

    def search_filters(self):
        search_param = self.request.GET.get('search_input')
        if not search_param:
            search_param = ','
        search_query = Q(username__icontains=search_param) | Q(email__icontains=search_param)
        return search_query


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class FollowUnfollowUser(generic.View):
    def get(self, request, user_id):
        follow_obj = request.user.following.filter(id=user_id)
        if follow_obj.exists():
            request.user.following.remove(user_id)
        else:
            request.user.following.add(user_id)
        return redirect('users:user_profile', user_id)


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class GetFollowingsList(generic.ListView):
    template_name = 'user_account/followers_following_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        username = self.kwargs.get('username')
        input_field = self.kwargs.get('input_field')
        if username:
            queryset = User.objects.filter(username=username)
            if queryset:
                if input_field == 'followings':
                    return queryset.first().following.all()
                elif input_field == 'followers':
                    return queryset.first().followers.all()
            else:
                return []
        return []


@method_decorator(decorator=(login_required, never_cache), name='dispatch')
class UserPinList(generic.ListView):
    template_name = 'user_account/user_pin_list.html'
    context_object_name = 'pins'

    def get_queryset(self):
        filter_params = Q(user__username=self.kwargs.get('username'))
        if self.kwargs.get('username') != self.request.user.username:
            filter_params = filter_params & Q(is_private=False)
        return Pin.objects.filter(filter_params).annotate(
            is_saved_pin=FilteredRelation('saved_pins', condition=Q(saved_pins__user_id=self.request.user.id))
        ).annotate(is_saved=F('is_saved_pin')).distinct()[:20]


class UserBoardPinList(PrivateBoardViewMixin, generic.ListView):
    template_name = 'user_account/user_board_pin_list.html'
    context_object_name = 'board_obj'

    def post(self, request, username, board_name):
        name = request.POST.get('name')
        board_obj = Board.objects.filter(name=name, user=request.user)
        is_private = request.POST.get('is_private')
        is_private = True if is_private in ['on', 'On', 'ON'] else False
        if not board_obj:
            Board.objects.filter(user__username=username, name=board_name).update(name=name, is_private=is_private)
        else:
            Board.objects.filter(user__username=username, name=board_name).update(is_private=is_private)
        return redirect('users:board_pins', request.user.username, name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['board_obj']:
            context['pins'] = context['board_obj'].pin.annotate(
                is_saved_pin=FilteredRelation('saved_pins', condition=Q(saved_pins__user_id=self.get_user_obj().id))
            ).annotate(is_saved=F('is_saved_pin'))
        return context

    def get_user_obj(self):
        username = self.kwargs.get('username')
        return User.objects.filter(username=username).first()

    def get_queryset(self):
        return self.get_object()

    def get_object(self):
        board_id = self.kwargs.get('board_name')
        username = self.kwargs.get('username')
        return Board.objects.filter(name=board_id, user__username=username).first()
