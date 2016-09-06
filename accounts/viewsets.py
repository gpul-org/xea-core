from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from .serializers import UserSerializer, UserPasswordSerializer
from .permissions import IsAdminOrSelf
from .models import UserProfile
from .serializers import UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'change_password':
            return UserPasswordSerializer
        if self.action == 'update_profile':
            return UserProfileSerializer
        else:
            return UserSerializer

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[IsAdminOrSelf])
    def change_password(self, request, pk=None):
        if not pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.get(pk=pk)
        self.check_object_permissions(request, user)
        serializer = UserPasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])

            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['put', 'patch'], permission_classes=[IsAdminOrSelf])
    def update_profile(self, request, pk=None):
        if not pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = self.get_object()
        profile = UserProfile.objects.get(user=user)
        self.check_object_permissions(request, user)
        serializer = UserProfileSerializer(data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.update(profile, serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
