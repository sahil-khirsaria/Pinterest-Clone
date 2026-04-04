from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from pinterest.models import Pin


@receiver(post_delete, sender=Pin)
def delete_pin_file_on_delete(sender, instance, **kwargs):
    """Delete the pin file from S3 when the Pin model instance is deleted."""
    if instance.pin_file:
        instance.pin_file.delete(save=False)


@receiver(pre_save, sender=Pin)
def delete_old_pin_file_on_update(sender, instance, **kwargs):
    """Delete the old pin file from S3 when a new file is uploaded."""
    if not instance.pk:
        return
    try:
        old_file = Pin.objects.get(pk=instance.pk).pin_file
    except Pin.DoesNotExist:
        return
    new_file = instance.pin_file
    if old_file and old_file != new_file:
        old_file.delete(save=False)