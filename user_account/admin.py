from django.contrib import admin

from user_account.models import User, UserProfile, ChatMessage


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProfile)
class UserProfileModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ChatMessage)
class ChatMessageModelAdmin(admin.ModelAdmin):
    pass
