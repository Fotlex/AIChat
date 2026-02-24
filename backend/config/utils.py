import orjson
from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware
from django.utils.module_loading import import_string


def scoped_middleware(middleware_paths, url_conf):
    patterns, app_name, namespace = url_conf

    decorators = [
        decorator_from_middleware(import_string(path))
        for path in reversed(middleware_paths)
    ]

    for pattern in patterns:
        for decorator in decorators:
            pattern.callback = decorator(pattern.callback)

    return patterns, app_name, namespace


R204 = HttpResponse(status=204)
R400 = HttpResponse(status=400)
R401 = HttpResponse(status=401)
R404 = HttpResponse(status=404)
R405 = HttpResponse(status=405)
R500 = HttpResponse(status=500)


def fast_json(data, status=200):
    return HttpResponse(
        orjson.dumps(data), content_type="application/json", status=status
    )
