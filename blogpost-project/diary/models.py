import cv2
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.urls import reverse
from .validators import MyUnicodeUsernameValidator, profanity
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

    last_request = models.DateTimeField(_("last request"), blank=True, null=True)

    def __init__(self, *args, **kwargs):
        self._meta.get_field(
            'username'
        ).validators[0] = MyUnicodeUsernameValidator()
        super().__init__(*args, **kwargs)

    # alternative way to override user validator:
    #
    # username = models.CharField(
    #     _("username"),
    #     max_length=150,
    #     unique=True,
    #     help_text=_(
    #         "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    #     ),
    #     validators=[MyUnicodeUsernameValidator()],
    #     error_messages={
    #         "unique": _("A user with that username already exists."),
    #     },
    # )


class Post(models.Model):
    title = models.CharField(max_length=100, validators=[profanity])
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(validators=[profanity])
    image = models.ImageField(upload_to='diary/images/', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            # Load the image using OpenCV
            img = cv2.imread(self.image.path)
            # Get the dimensions of the image
            height, width = img.shape[:2]
            # Set the maximum size of the image
            max_size = 2000
            # Determine the scaling factor to use for resizing the image
            if height > max_size or width > max_size:
                scale_factor = max_size / max(height, width)
            else:
                scale_factor = 1
            # Resize the image using the scaling factor
            resized_img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor)
            # Save the resized image to the original file path
            cv2.imwrite(self.image.path, resized_img)

    class Meta:
        ordering = ['-updated']

    def __str__(self) -> str:
        return f'{self.author.username}: {self.title}'
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.id})


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'post'], name='unique_like')]

    def __str__(self) -> str:
        return f'{self.user.username}: {self.post.title}'

