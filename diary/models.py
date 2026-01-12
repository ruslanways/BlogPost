import cv2
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.urls import reverse
from .validators import MyUnicodeUsernameValidator, profanity
from django.utils.translation import gettext_lazy as _
from pathlib import Path


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
    thumbnail = models.ImageField(upload_to='diary/images/thumbnails/', blank=True, null=True, editable=False, max_length=200)
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
            max_size = 2000

            # Determine the scaling factor to use for resizing the image
            if height > max_size or width > max_size:
                scale_factor = max_size / max(height, width)
                resized_img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor)
            else:
                resized_img = img

            # Save the resized image to the original file path
            cv2.imwrite(self.image.path, resized_img)


            ##########################################
            # Generate the thumbnail image

            thumbnail_size = (300, 300)

            thumbnail_width, thumbnail_height = thumbnail_size
            desired_aspect_ratio = thumbnail_width / thumbnail_height
            original_aspect_ratio = width / height

            # Calculate the scaling factor for resizing the image to fit the thumbnail
            if desired_aspect_ratio > original_aspect_ratio:
                scale_factor = thumbnail_width / width
            else:
                scale_factor = thumbnail_height / height

             # Calculate the new dimensions of the thumbnail
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)

            # Resize the image while maintaining the original aspect ratio
            thumbnail_resized_img = cv2.resize(resized_img, (new_width, new_height))

            # Calculate the cropping box to center the resized image in the thumbnail
            x_offset = (new_width - thumbnail_width) // 2
            y_offset = (new_height - thumbnail_height) // 2

             # Crop the resized image to fit the thumbnail area (object-fit: cover)
            cropped_img = thumbnail_resized_img[y_offset:y_offset + thumbnail_height, x_offset:x_offset + thumbnail_width]

            # Get the directory path for thumbnails
            thumbnail_dir = Path(settings.MEDIA_ROOT) / 'diary/images/thumbnails'
            thumbnail_dir.mkdir(parents=True, exist_ok=True)

            # Get the original filename
            original_filename = Path(self.image.name).name

            # Generate the thumbnail path
            thumbnail_path = thumbnail_dir / original_filename

            # Save the thumbnail image
            cv2.imwrite(str(thumbnail_path), cropped_img)

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

