from rest_framework.decorators import (api_view, permission_classes,
    renderer_classes)
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework_swagger.renderers import (OpenAPIRenderer,
    SwaggerUIRenderer)


@api_view()
@permission_classes((AllowAny, ))
@renderer_classes((OpenAPIRenderer, CoreJSONRenderer, SwaggerUIRenderer, ))
def schema_view(request):
    generator = SchemaGenerator(title='XEA API')
    return Response(generator.get_schema(request=request))
