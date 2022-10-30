from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import string
from pathlib import Path



class MyUnicodeUsernameValidator(UnicodeUsernameValidator):
     message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and @ . + - _ characters."
    )


def profanity(content):
    with open(Path(__file__).resolve().parent / "profanity/bad-words.txt") as f:
        profanity_set = set(f.read().split())
    if profanity_set & set([word.strip(string.punctuation) for word in content.split()]):
        raise ValidationError(
            _('Using profanity prohibited, please correct the content!'),
            code='invalid',
        )
