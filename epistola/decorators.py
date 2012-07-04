# vim: set ts=4 sw=4 sts=4 et ai:
from functools import wraps
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponsePermanentRedirect
from django.utils import simplejson
from django.utils.decorators import method_decorator


def json_response(func):
    '''
    Decorator that returns the response as a json object.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        json_response = HttpResponse(content_type='application/json')

        if isinstance(response, HttpResponse):
            json_response.cookies = response.cookies
            json_response.status_code = response.status_code
            if isinstance(response, (HttpResponseRedirect,
                HttpResponsePermanentRedirect)):
                json = {'redirect': response['Location']}
            else:
                json = {'html': response.content}
        else:
            json = response

        json_response.write(simplejson.dumps(json))
        return json_response
    return wrapper


class JsonResponseMixin(object):
    '''
    Mixin that returns the response as a json object.
    '''
    @method_decorator(json_response)
    def dispatch(self, *args, **kwargs):
        return super(JsonResponseMixin, self).dispatch(*args, **kwargs)
