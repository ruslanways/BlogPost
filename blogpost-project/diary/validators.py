from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class MyUnicodeUsernameValidator(UnicodeUsernameValidator):
     message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and @ . + - _ characters."
    )

