from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.urls import reverse
from .validators import MyUnicodeUsernameValidator, profanity
from django.utils.translation import gettext_lazy as _
from pathlib import Path
from PIL import Image, ImageOps


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
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[MyUnicodeUsernameValidator()],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )


class Post(models.Model):
    title = models.CharField(max_length=100, validators=[profanity])
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(validators=[profanity])
    image = models.ImageField(upload_to='diary/images/', blank=True)
    thumbnail = models.ImageField(upload_to='diary/images/thumbnails/', blank=True, null=True, editable=False, max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if self.image:
            with Image.open(self.image.path) as img:
                img_format = img.format
                max_size = (2000, 2000)

                img_copy = img.copy()
                img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
                img_copy.save(self.image.path, format=img_format)

                ##########################################
                # Generate the thumbnail image

                thumbnail_size = (300, 300)
                thumb_img = ImageOps.fit(
                    img_copy,
                    thumbnail_size,
                    method=Image.Resampling.LANCZOS,
                    centering=(0.5, 0.5),
                )

                # Get the directory path for thumbnails
                thumbnail_dir = Path(settings.MEDIA_ROOT) / 'diary/images/thumbnails'
                thumbnail_dir.mkdir(parents=True, exist_ok=True)

                # Get the original filename
                original_filename = Path(self.image.name).name

                # Generate the thumbnail path
                thumbnail_path = thumbnail_dir / f"thumb_{original_filename}"

                # Save the thumbnail image
                thumb_img.save(thumbnail_path, format=img_format)

                # Calculate the relative path of the thumbnail image
                thumbnail_rel_path = thumbnail_path.relative_to(settings.MEDIA_ROOT)

                # Update the thumbnail field in the database
                self.thumbnail.name = str(thumbnail_rel_path)
                super().save(update_fields=['thumbnail'], *args, **kwargs)

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
