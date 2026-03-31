from django.contrib import admin

from pinterest.models import Category, Pin, SavedPin, Board


@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Pin)
class PinModelAdmin(admin.ModelAdmin):
    pass


@admin.register(SavedPin)
class SavedPinModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Board)
class BoardModelAdmin(admin.ModelAdmin):
    pass
