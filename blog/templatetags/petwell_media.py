from django import template

from blog.media import image_url

register = template.Library()
register.filter("image_url", image_url)
