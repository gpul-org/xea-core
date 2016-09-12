from rest_framework.decorators import (api_view, permission_classes,
                                       renderer_classes)
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_swagger.renderers import (OpenAPIRenderer,
                                              SwaggerUIRenderer)

from .schemas import SchemaGenerator


@api_view()
@permission_classes((AllowAny, ))
@renderer_classes((OpenAPIRenderer,
                   CoreJSONRenderer,
                   SwaggerUIRenderer, ))
def schema_view(request):
    generator = SchemaGenerator(title='XEA API')
    return Response(generator.get_schema(request=request))


@api_view()
def api_root(request, format=None):
    return Response({'message': 'Welcome to XEA'})
    return Response({
        '_self': reverse(
            'root', request=request, format=format),
        '_links': {
            'docs': reverse(
                'swagger-ui', request=request, format=format),
            'auth': {
                'jwt': reverse(
                    'jwt_knox-get-token', request=request, format=format),
            },
        },
    })
