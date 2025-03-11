import json
from django import template
from django.contrib.auth.models import Group
from django.utils.html import urlize
from django.utils.formats import date_format
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe



# Define template tags to use on the templates
register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    '''Check if the user belongs to a group'''
    return user.groups.filter(name=group_name).exists()

@register.filter(name='has_permission')
def has_permission(user, permission_codename):
    '''Check if the user has a specific permission'''
    return user.has_perm(permission_codename)

@register.filter(name='full_name')
def full_name(user):
    '''Return the user's full name'''
    return user.get_full_name() or user.username

@register.filter(name='format_date')
def format_date(value, format_string="DATE_FORMAT"):
    '''Format a datetime object to a more readable format'''
    return date_format(value, format_string)

@register.filter(name='jsonify')
def jsonify(value):
    '''Convert Python objects to JSON strings'''
    return mark_safe(json.dumps(value, cls=DjangoJSONEncoder))