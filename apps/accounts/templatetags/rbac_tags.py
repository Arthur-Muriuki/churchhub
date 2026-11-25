from django import template

register = template.Library()


@register.filter(name="has_perm")
def has_perm(user, perm_code):
    """
    Usage in templates: {% if request.user|has_perm:"pastoral.view_confidential" %}
    """
    if not user or not user.is_authenticated:
        return False
    return user.has_role_perm(perm_code)