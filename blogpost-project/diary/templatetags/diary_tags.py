from atexit import register
from django import template
from diary.models import *

register = template.Library()


@register.simple_tag
def like_or_unlike(author, post):
    return '&#10084;' if author.like_set.all() & post.like_set.all() else '&#9825;'

