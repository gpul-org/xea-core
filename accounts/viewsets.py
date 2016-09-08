from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from .serializers import UserSerializer, UserPasswordSerializer
from .permissions import IsAdminOrSelf
from .models import UserProfile
from .serializers import UserProfileSerializer
from . import utils


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

    @detail_route(methods=['get'], permission_classes=[IsAdminOrSelf])
    def activate(self, request, upk=None, token=None):
        # First, if client is accessing to the activation url's root we have to refuse his request
        if upk is None or token is None:
            return Response({'msg': 'This activation link is not valid'}, status=status.HTTP_403_FORBIDDEN)
        # Then we start validating those two fields
        try:
            user = self.get_user_to_activate(upk)
        except get_user_model().DoesNotExist:
            return Response({'msg': 'This activation link is not valid'}, status=status.HTTP_400_BAD_REQUEST)

        # Now validate the token
        if utils.validate_token(user, token):  # If it's valid we can start activation process
            return self.activate_user(user)

        # Otherwise we send a 400
        return Response({},
                        status=status.HTTP_400_BAD_REQUEST)

    def activate_user(self, user):
        if user.is_active:  # If the user is using an activation link being already active we send a 403
            return Response({},
                            status=status.HTTP_403_FORBIDDEN)
        else:  # Otherwise we can activate the account
            user.is_active = True
            user.save()
            return Response({'msg': 'The account had been activated correctly'},
                            status=status.HTTP_204_NO_CONTENT)

    def get_user_to_activate(self, upk):
        user = get_user_model().objects.get(pk=upk)
        return user
