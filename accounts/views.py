from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from . import serializers
from . import utils


class ActivateUserView(APIView):
    model = get_user_model()
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.UserSerializer

    def get(self, request, upk=None, token=None):
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
