# Copyright 2023, themeontology.org
# Tests:
from django import http


class CloudMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_request(self, request):
        if 'HTTP_X_FORWARDED_PROTO' in request.META:
            if request.META['HTTP_X_FORWARDED_PROTO'] == 'https':
                request.is_secure = lambda: True
                return None

        host = request.get_host()
        if host.find('themeontology.org') >= 0:
            new_url = 'https://%s%s' % (host, request.get_full_path())
            return http.HttpResponsePermanentRedirect(new_url)

        return None
