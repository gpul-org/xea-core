import coreapi
from copy import copy
from rest_framework import status
from rest_framework.schemas import SchemaGenerator as BaseSchemaGenerator
from rest_framework.compat import urlparse

def responds_desired(*args, **kwargs):
    """We dont know yet how to implement this.
    """
    def decorator(func):
        return func
    return decorator


def responds(message, status=status.HTTP_200_OK, **kwargs):
    """Documents the status code per handled case.

    Additional parameters may make it into the OpenAPI documentation
    per view. Examples of those parameters include
    examples={'application/json': <example>} or
    schema=<schema-definition>. As schemata are needed in order to
    render the examples in the Web UI, an error will be signaled if
    examples= are provided without a schema= parameter.

    Schemas can be easily built by using this function's helpers:
    responds.schemas.obj for constructing objects,
    responds.schemas.string for constructing strings, and
    responds.props for providing properties to an object.

    In the future, more of those may be developed, or even other ways
    of getting this information in a more centralized way.

    """
    if status is None:
        status = 'default'

    obj = {}
    obj['description'] = message

    for key in kwargs.keys():
        obj[key] = kwargs[key]

    def decorator(func):
        if not hasattr(func, '_responses'):
            func._responses = {}
        func._responses[status] = obj
        return func
    return decorator


def schema_object(title, properties=[]):
    """This helper allows to construct a schema object. A schema object has a title, and properties.

    This helper will take care automatically of whether properties are
    required, if those properties were specified using responds.props
    helper.

    """
    obj = {}
    if title: obj['title'] = title
    obj['type'] = 'object'
    obj['properties'] = { prop.title: prop.args for prop in properties }
    obj['required'] = [ prop.title for prop in properties if prop.required ]

    return obj

def schema_property(title, other, required=True):
    """This helper allows to specify properties which are by default
    required (but that can be changed via required=False). The second
    argument receives the type of the property getting
    defined. Usually a string or another object.

    """
    obj = lambda: None
    obj.title = title
    obj.args = other
    obj.required = required
    return obj

responds.schemas = lambda: None
responds.schemas.obj = schema_object
responds.props = schema_property

## Trivial types do not even have a docstring
responds.schemas.string = lambda: { 'type': 'string' }
responds.schemas.int = lambda: { 'type': 'int' }



class SchemaGenerator(BaseSchemaGenerator):
    """This patched SchemaGenerator gets additional data which has no use
    in CoreAPI, but that can be represented in OpenAPI/Swagger. With
    additional help from the OpenAPI encoder, we can receive that
    additional data in a OpenAPI context.

    """
    def get_link(self, path, method, callback, view):
        """
        Return a `coreapi.Link` instance for the given endpoint.
        """
        fields = self.get_path_fields(path, method, callback, view)
        fields += self.get_serializer_fields(path, method, callback, view)
        fields += self.get_pagination_fields(path, method, callback, view)
        fields += self.get_filter_fields(path, method, callback, view)

        if fields and any([field.location in ('form', 'body') for field in fields]):
            encoding = self.get_encoding(path, method, callback, view)
        else:
            encoding = None

        description = self.get_description(path, method, callback, view)

        link = coreapi.Link(
            url=urlparse.urljoin(self.url, path),
            action=method.lower(),
            encoding=encoding,
            description=description,
            fields=fields,
            transform=None, # Not handled, but here for future reference
        )

        link._responses = self.get_responses(path, method, callback, view)
        link._produces = self.get_produces(path, method, callback, view)

        return link

    def _get_actual_view(self, method, callback, view, default=True):
        if hasattr(callback, 'actions'):
            action_name = callback.actions[method.lower()]
            action = getattr(view, action_name)
            return action
        else:
            return view if default else None

    def get_responses(self, path, method, callback, view):
        ## Get generic responses
        responses = {}
        if hasattr(view, '_responses'):
            responses = copy(view._responses)
            pass

        action = self._get_actual_view(method, callback, view, default=False)
        if action and hasattr(action, '_responses'):
            responses.update(action._responses)
        return responses or None

    def get_produces(self, path, method, callback, view):
        return ["application/json", "application/xml"]

    def get_description(self, path, method, callback, view):
        action = self._get_actual_view(method, callback, view, default=False)
        if action and action.__doc__:
            return self._get_description(view, action)
        else:
            return self._get_description(view, None)

    def _get_description(self, view, action=None):
        def unwrap(s):
            if s:
                return "\n".join([l.strip() for l in s.strip().splitlines()])
            else:
                return ""

        generic = view.__doc__
        specific = action.__doc__

        if specific:
            specific += "\n\n"

        return "{1}{0}".format(unwrap(generic),
                               unwrap(specific))


def get_responses(link):
    """Returns documented responses based on the @responds decorator.

    In case no documentation exists, the empty object is returned,
    instead of a default, which better represents that behavior not to
    be formally documented.

    """
    if link._responses:
        return link._responses

    return {}

## Monkey-patch encode
# We need to do this so that the openapi_codec will receive our additional elements.
from openapi_codec import encode
encode._get_responses = get_responses

# We need to patch get_operation if we want openapi to also give us
# the opportunity to speak about different return formats.
def get_operation(tag, link):
    return {
        'tags': [tag],
        'description': link.description,
        'responses': encode._get_responses(link),
        'produces': get_produces(link),
        'parameters': encode._get_parameters(link.fields)
    }
encode._get_operation = get_operation

def get_produces(link):
    if hasattr(link, '_produces'):
        return link._produces
