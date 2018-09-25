from django import template

register = template.Library()

@register.filter()
def pdb_trace(value):
    import pdb; pdb.set_trace()
