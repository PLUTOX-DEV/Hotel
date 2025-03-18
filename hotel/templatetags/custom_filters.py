from django import template

register = template.Library()

@register.filter(name='capitalize_words')
def capitalize_words(value):
    """Capitalizes the first letter of each word in a string."""
    if not isinstance(value, str):  # Ensure value is a string
        value = str(value)
    return ' '.join(word.capitalize() for word in value.split())


@register.filter
def add_suffix(value, suffix="!"):
    """Adds a suffix to a string."""
    return f"{value}{suffix}"
