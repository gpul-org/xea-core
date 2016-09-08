from django.contrib.auth import get_user_model
from rest_framework import serializers
from .utils import send_activation_mail
from .models import UserProfile


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'gender', 'birthday', 'nationality', 'location')

    def update(self, instance, validated_data):
        instance.gender = validated_data.get('gender', instance.gender)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.nationality = validated_data.get('nationality', instance.nationality)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = get_user_model()
        fields = ('url', 'username', 'password', 'email', 'first_name', 'last_name', 'profile')
        write_only_fields = ('password',)

    def create(self, validated_data):
        """
        Here the new User object is created.
        At the end of the process we will send and activation mail to the user's email address
            """
        user = get_user_model().objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False
        )

        user.set_password(validated_data['password'])
        user.save()
        send_activation_mail(user)
        return user


class UserPasswordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'password')
