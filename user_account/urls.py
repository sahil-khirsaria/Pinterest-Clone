from django.urls import path

from user_account.views import (
    UserProfileView, UserSearchView, UserUpdateView, UserDeleteView, FollowUnfollowUser, UserPasswordChangeView,
    UserEmailVerification, UserPasswordResetView, UserPasswordResetConfirmView, UserPasswordResetDoneView,
    UserPasswordResetCompleteView, GetFollowingsList, UserPinList, UserBoardPinList
)

app_name = 'users'

urlpatterns = [
    path('email-verification/<uid>/<token>', UserEmailVerification.as_view(), name='user_email_verification'),
    path('search', UserSearchView.as_view(), name='user_search'),
    path('delete-account/<str:username>', UserDeleteView.as_view(), name='delete_account'),
    path('profile/<int:id>', UserProfileView.as_view(), name='user_profile'),
    path('edit-profile/<str:username>', UserUpdateView.as_view(), name='edit_user'),
    path('follow-unfollow/<int:user_id>', FollowUnfollowUser.as_view(), name='follow_unfollow'),
    path(
        'followers-followings/<str:username>/<str:input_field>',
        GetFollowingsList.as_view(),
        name='followers_followings'
    ),
    path('change-password', UserPasswordChangeView.as_view(), name='change_password'),

    path('password-reset', UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('<str:username>/pins', UserPinList.as_view(), name='user_pins'),

    path('<str:username>/<str:board_name>/pins', UserBoardPinList.as_view(), name='board_pins')
]
