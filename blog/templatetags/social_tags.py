from django import template
from home.models import SocialItems

register = template.Library()


@register.inclusion_tag('tags/social.html', takes_context=True)
def social_items(context):
    context = {'items': SocialItems.objects.all()}
    return context