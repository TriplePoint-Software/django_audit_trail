import sys
import itertools


def get_request(exact_keys=None):
    """ Walks through frames and search for 'request' object.

    :Parameters:
        `exact_keys` - request should contain list of keys
    :Return:
        request object or None
    """
    request = None

    for i in itertools.count():
        try:
            frame = sys._getframe(i)
        except ValueError:
            break
        if not frame:
            break

        if 'request' in frame.f_locals:
            request = frame.f_locals['request']

            # pylint: disable=W0110
            if all(map(lambda x: hasattr(request, x), exact_keys or [])):
                return request

    return request
