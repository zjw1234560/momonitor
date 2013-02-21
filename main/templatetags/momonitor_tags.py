from django import template
from django.core.urlresolvers import reverse
import time
import logging
register = template.Library()

from momonitor.main.constants import (STATUS_GOOD,
                                      STATUS_BAD,
                                      STATUS_UNKNOWN)

def percentage(value):
    value*=100
    return ("%s" % int(value)) + "%"

def multiply(value,factor):
    return value*factor

def negate(value):
    return -value

def resource_url(instance):
    resource_name = instance.__class__.resource_name
    return "/api/v1/%s/%s/" % (resource_name,instance.id)
    
def since(value):
    if not type(value)==float:
        try:
            value = float(value)
        except:
            logging.debug("Cannot parse value %s with templatetag since" % value)
            return "unknown"
    seconds_since = int(time.time()-value)
    if seconds_since > 60*60*24:
        return "%s day(s) ago" % (seconds_since/(60*60*24))
    elif seconds_since > 60*60:
        return "%s hour(s) ago" % (seconds_since/(60*60))
    elif seconds_since > 60:
        return "%s minute(s) ago" % (seconds_since/60)
    elif seconds_since > 1:
        return "%s second(s) ago" % seconds_since
    else:
        return "just now"

def to_bootstrap_rowclass(value):    
    if value==STATUS_GOOD:
        return "success"
    elif value==STATUS_BAD:
        return "error"
    else:
        return "warning"

def to_bootstrap_progressbarclass(value):    
    if value==STATUS_GOOD:
        return "bar-success"
    elif value==STATUS_BAD:
        return "bar-danger"
    else:
        return "bar-warning"

register.filter('since', since)
register.filter('percentage', percentage)
register.filter('multiply', multiply)
register.filter('negate', negate)
register.filter('to_bootstrap_rowclass', to_bootstrap_rowclass)
register.filter('to_bootstrap_progressbarclass', to_bootstrap_progressbarclass)
register.filter('resource_url', resource_url)
