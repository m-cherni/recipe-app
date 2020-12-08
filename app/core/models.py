import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from django.conf import settings


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe"""
    extention = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{extention}'

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """creates and saves a new user"""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates a nes superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(_("Email"), max_length=254, unique=True)
    name = models.CharField(_("Name"), max_length=50)
    is_active = models.BooleanField(_("Is Active"), default=True)
    is_staff = models.BooleanField(_("Is Staff"), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag model fields"""
    name = models.CharField(_("Name"), max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_("User"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("")
        verbose_name_plural = _("s")

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("_detail", kwargs={"pk": self.pk})


class Ingredient(models.Model):
    """Ingredient to be used in recipe"""
    name = models.CharField(_("Name"), max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_("User"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("")
        verbose_name_plural = _("s")

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_("User"), on_delete=models.CASCADE)
    title = models.CharField(_("Title"), max_length=50)
    time_minutes = models.IntegerField(_("Time minutes"))
    price = models.DecimalField(_("Price"), max_digits=5, decimal_places=2)
    link = models.CharField(_("Link"), max_length=255, blank=True)
    ingredients = models.ManyToManyField("Ingredient", verbose_name=_(""))
    tags = models.ManyToManyField("Tag", verbose_name=_(""))
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    class Meta:
        verbose_name = _('')
        verbose_name_plural = _('s')

    def __str__(self):
        return self.title
