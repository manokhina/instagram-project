import base64
import functools
import hashlib
import hmac
import random
import sys
import time

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


if sys.version_info < (3,):
    integer_types = (int, long)
    unicode_type = unicode
else:
    integer_types = (int,)
    unicode_type = str


quote = functools.partial(quote, safe='~')


class SimpleAuth(object):
    def __init__(self, key):
        self.key = key

    def authorize(self, method, url, params=None):
        return 'CloudSight %s' % self.key


class OAuth(object):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def authorize(self, method, url, params=None):
        nonce = str(random.random()).encode('utf8')
        oauth_params = {
            'oauth_consumer_key': self.key,
            'oauth_nonce': hashlib.sha1(nonce).hexdigest(),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': int(time.time()),
            'oauth_version': '1.0',
        }

        if params:
            oauth_params.update(params)

        encoded = []

        for key, value in oauth_params.items():
            if isinstance(value, integer_types):
                value = str(value)
            if isinstance(value, unicode_type):
                value = value.encode('utf8')
            encoded.append((quote(key), quote(value)))

        encoded.sort()
        encoded = '&'.join('%s=%s' % (key, value) for key, value in encoded)
        base_string = '%s&%s&%s' % (method.upper(), quote(url), quote(encoded))
        base_string = base_string.encode('utf8')
        signing_key = '%s&' % quote(self.secret)
        signing_key = signing_key.encode('utf8')

        signature = hmac.new(signing_key, base_string, hashlib.sha1).digest()
        oauth_params['oauth_signature'] = base64.b64encode(signature)

        header_params = []

        for key, value in oauth_params.items():
            if not key.startswith('oauth_'):
                continue
            if isinstance(value, integer_types):
                value = str(value)
            if isinstance(value, unicode_type):
                value = value.encode('utf8')
            header_params.append((quote(key), quote(value)))

        header_params.sort()
        header = ', '.join(
            '%s="%s"' % (key, value) for key, value in header_params)
        return 'OAuth %s' % header
