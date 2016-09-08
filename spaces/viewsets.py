from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from api.permissions import IsPlaceOwnerOrStaff
from .models import Place
from .serializers import PlaceSerializer


class PlaceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows 'spaces' to be viewed or edited.
    """
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

    @detail_route(methods=['put','patch'], permission_classes=[IsPlaceOwnerOrStaff])
    def update_place_data(self, request, pk=None):
        if not pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = self.get_object()
        place = Place.objects.get(pk=pk)
        self.check_object_permissions(request, user)
        serializer = PlaceSerializer(data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.update(place, serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
