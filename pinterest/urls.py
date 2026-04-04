from django.urls import path

from pinterest.views import (
    PinCreateView, PinUpdateView, PinDeleteView, PinDetailView, SaveUnsavePin,
    SearchPinByCategoryListView, PinAddToBoard, DeleteBoard,
    MakePublicPrivateBoard, RemovePinFromBoard, LikeUnlikePin, AddComment, DeleteComment
)

app_name = 'pins'
urlpatterns = [
    path('pin/create/<str:input_value>', PinCreateView.as_view(), name='create_pin'),
    path('pin/edit/<int:id>', PinUpdateView.as_view(), name='edit_pin'),
    path('pin/delete/<int:id>', PinDeleteView.as_view(), name='delete_pin'),
    path('pin/details/<int:id>', PinDetailView.as_view(), name='detail_pin'),

    path('pin/save-unsave-pin/<int:pin_id>', SaveUnsavePin.as_view(), name='save_unsave_pin'),
    path('pin/like-unlike/<int:pin_id>', LikeUnlikePin.as_view(), name='like_unlike_pin'),

    path('pin/comment/<int:pin_id>', AddComment.as_view(), name='add_comment'),
    path('pin/delete-comment/<int:comment_id>', DeleteComment.as_view(), name='delete_comment'),

    path('pin/search-category', SearchPinByCategoryListView.as_view(), name='search_pin_by_category'),

    path('pin/<int:board_id>/<int:pin_id>', PinAddToBoard.as_view(), name='pin_add_to_board'),

    path('delete-board/<int:board_id>', DeleteBoard.as_view(), name='delete_board'),

    path('public-private-board/<int:board_id>', MakePublicPrivateBoard.as_view(), name='public_private_board'),

    path(
        'remove-pin-from-board/<int:board_id>/<int:pin_id>', RemovePinFromBoard.as_view(), name='remove_pin_from_board'
    ),
]
