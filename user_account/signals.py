from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from user_account.models import UserProfile


@receiver(post_delete, sender=UserProfile)
def delete_profile_files_on_delete(sender, instance, **kwargs):
    """Delete profile and cover pictures from S3 when UserProfile is deleted."""
    if instance.profile_picture:
        instance.profile_picture.delete(save=False)
    if instance.cover_picture:
        instance.cover_picture.delete(save=False)


@receiver(pre_save, sender=UserProfile)
def delete_old_profile_files_on_update(sender, instance, **kwargs):
    """Delete old pictures from S3 when new ones are uploaded."""
    if not instance.pk:
        return
    try:
        old_instance = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        return
    if old_instance.profile_picture and old_instance.profile_picture != instance.profile_picture:
        old_instance.profile_picture.delete(save=False)
    if old_instance.cover_picture and old_instance.cover_picture != instance.cover_picture:
        old_instance.cover_picture.delete(save=False)