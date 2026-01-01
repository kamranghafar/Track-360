from django import template
import json
from decimal import Decimal
from ..views import DecimalEncoder

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Add a CSS class to a form field.

    Usage: {{ form.field|add_class:"form-control" }}
    """
    css_classes = value.field.widget.attrs.get('class', '')
    if css_classes:
        css_classes = f"{css_classes} {arg}"
    else:
        css_classes = arg
    return value.as_widget(attrs={'class': css_classes})

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get an item from a dictionary using its key.

    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key, '')

@register.filter(name='to_json')
def to_json(value):
    """
    Convert a Python object to a JSON string.

    Usage: {{ data|to_json }}
    """
    return json.dumps(value, cls=DecimalEncoder)

@register.filter(name='extract_values')
def extract_values(data_list, key):
    """
    Extract values for a specific key from a list of dictionaries or model instances.

    Usage: {{ data_list|extract_values:'key' }}
    """
    values = []
    for item in data_list:
        if hasattr(item, 'get') and callable(item.get):
            # Item is dictionary-like
            values.append(item.get(key, ''))
        else:
            # Item is a model instance or other object
            values.append(getattr(item, key, ''))
    return values

@register.filter(name='extract_values_json')
def extract_values_json(data_list, key):
    """
    Extract values for a specific key from a list of dictionaries or model instances and convert to JSON.

    Usage: {{ data_list|extract_values_json:'key' }}
    """
    values = []
    for item in data_list:
        if hasattr(item, 'get') and callable(item.get):
            # Item is dictionary-like
            values.append(item.get(key, ''))
        else:
            # Item is a model instance or other object
            values.append(getattr(item, key, ''))
    return json.dumps(values, cls=DecimalEncoder)


@register.simple_tag
def url_replace(request, field, value):
    """
    Replace or add a parameter to the current URL.

    Usage: {% url_replace request 'page' 2 %}
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.filter(name='split')
def split(value, arg):
    """
    Split a string by a delimiter.

    Usage: {{ string|split:"," }}
    """
    return value.split(arg)


@register.filter(name='index')
def index(value, arg):
    """
    Get an item from a list by index.

    Usage: {{ list|index:0 }}
    """
    try:
        return value[int(arg)]
    except (IndexError, ValueError, TypeError):
        return ''
