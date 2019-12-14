def marshal_with_schema(schema):
    def decorator(func):
        def inner(self):
            # Validate
            if schema == 0:
                return {'error': 'Cant be 0'}
            # Parse
            data = schema * 10
            # Continue
            return func(self, data)
        return inner
    return decorator


@marshal_with_schema(1)
def post(self, data):
    return {'Complete': data}


print(post('A'))
