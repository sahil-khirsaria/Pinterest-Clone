from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.helper_methods import update_user_profile_picture_name, update_user_cover_picture_name


class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', "Others"),
        ('N', 'Not Specified')
    )

    email = models.EmailField(verbose_name=_('Email Address'), unique=True, null=False)
    following = models.ManyToManyField(
        verbose_name=_("Following"), to='self', related_name='followers', symmetrical=False
    )
    gender = models.CharField(verbose_name=_('Gender'), max_length=1, choices=GENDER_CHOICES, default='N')
    interest = models.ManyToManyField(verbose_name=_('Interest'), to='pinterest.Category')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.first_name, self.last_name = self.first_name.title(), self.last_name.title()
        return super(User, self).save(*args, **kwargs)

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def total_followers(self):
        return self.followers.count()

    @property
    def total_following(self):
        return self.following.count()

    @property
    def total_private_pins(self):
        return self.pins.filter(is_private=True).count()

    @property
    def total_public_pins(self):
        return self.pins.filter(is_private=False).count()

    @property
    def total_pins(self):
        return self.total_private_pins + self.total_public_pins

    @property
    def total_saved(self):
        return self.saved_pins.count()

    @property
    def total_public_boards(self):
        return self.boards.count()


class UserProfile(models.Model):
    user = models.OneToOneField(
        verbose_name=_('User'), to='User', related_name='user_profile', on_delete=models.CASCADE
    )
    about = models.TextField(verbose_name=_('About'), default='', blank=True)
    profile_picture = models.ImageField(
        verbose_name=_('Profile Picture'), null=True, blank=True, upload_to=update_user_profile_picture_name
    )
    cover_picture = models.ImageField(
        verbose_name=_('Cover Picture'), null=True, blank=True, upload_to=update_user_cover_picture_name
    )
    website = models.URLField(verbose_name=_('Website'), default='', blank=True)
    country = models.CharField(verbose_name=_('Country'), max_length=150, default='', blank=True)
    language = models.CharField(verbose_name=_('Language'), max_length=150, default='', blank=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'Users Profile'

    def __str__(self):
        return self.user.username
