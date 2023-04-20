from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.helper_methods import update_pin_file_name

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'), auto_now=True)

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(verbose_name=_('Category'), max_length=150, unique=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name.title()
        return super(Category, self).save(force_insert=False, force_update=False, using=None, update_fields=None)


class Pin(BaseModel):
    PIN_STATUS = (
        (0, 'Draft'),
        (1, 'Uploaded'),
        (2, 'Deleted')
    )

    title = models.CharField(verbose_name=_('Title'), max_length=65)
    status = models.PositiveSmallIntegerField(verbose_name=_('Status'), default=1, choices=PIN_STATUS)
    user = models.ForeignKey(verbose_name=_('Uploaded By'), to=User, on_delete=models.CASCADE, related_name='pins')
    pin_file = models.FileField(verbose_name=_('Pin'), upload_to=update_pin_file_name)
    about = models.CharField(verbose_name=_('About'), max_length=250)
    alter_text = models.TextField(verbose_name=_('Alter Text'), null=True, blank=True)
    destination_link = models.URLField(verbose_name=_('Download from URL'), max_length=1000, null=True, blank=True)
    category = models.ManyToManyField(verbose_name=_('Categories'), to=Category )
    is_idea = models.BooleanField(verbose_name=_('Is Idea Pin'), default=False)
    is_private = models.BooleanField(verbose_name=_('Is Private Pin'), default=False)
    class Meta:
        verbose_name = 'Pin'
        verbose_name_plural = 'Pins'

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.title.title()
        return super(Pin, self).save(force_insert=False, force_update=False, using=None, update_fields=None)


class SavedPin(models.Model):
    user = models.ForeignKey(verbose_name=_('User'), to=User, on_delete=models.CASCADE, related_name='saved_pins')
    pin = models.ForeignKey(verbose_name=_('Pin'), to=Pin, on_delete=models.CASCADE, related_name='saved_pins')
    created_at = models.DateTimeField(verbose_name=_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = 'Saved Pin'
        verbose_name_plural = 'Saved Pins'
        unique_together = ('user', 'pin')

    def __str__(self):
        return f'{self.user.username} --- {self.pin.title}'


class Board(BaseModel):
    name = models.CharField(verbose_name=_('Name'), max_length=50)
    user = models.ForeignKey(verbose_name=_('User'), to=User, on_delete=models.CASCADE, related_name='boards')
    pin = models.ManyToManyField(verbose_name=_('Pin'), to=Pin)
    is_private = models.BooleanField(verbose_name=_('Is Private'), default=False)

    class Meta:
        verbose_name = 'Board'
        verbose_name_plural = 'Boards'
        unique_together = ('user', 'name')

    def __str__(self):
        return f'{self.user.username} --> {self.name}'

    @property
    def is_private_verbose(self):
        return 'on' if self.is_private else ''

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name.title()
        return super(Board, self).save(force_insert=False, force_update=False, using=None, update_fields=None)