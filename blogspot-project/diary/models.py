from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from .validators import MyUnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):

    # make email field unique and required (not blank)

    email = models.EmailField(
        _("email address"), 
        unique=True,  
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    def __init__(self, *args, **kwargs):
        self._meta.get_field(
            'username'
        ).validators[0] = MyUnicodeUsernameValidator()
        super().__init__(*args, **kwargs)

    # alternative way to override user validator:
    #     
    # username_validator = MyUnicodeUsernameValidator()
    #
    # username = models.CharField(
    #     _("username"),
    #     max_length=150,
    #     unique=True,
    #     help_text=_(
    #         "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    #     ),
    #     validators=[username_validator],
    #     error_messages={
    #         "unique": _("A user with that username already exists."),
    #     },
    # )


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='diary/images/', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self) -> str:
        return f'{self.author.username}: {self.title}'


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'post'], name='unique_like')]

    def __str__(self) -> str:
        return f'{self.user.username}: {self.post.title}'

