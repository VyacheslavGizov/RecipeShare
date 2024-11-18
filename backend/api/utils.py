def request_in_serializer_context(serialiser):
    request = serialiser.context.get('request', None)
    return request is not None
   # может грамотно дописать с исключением и аннотацией
