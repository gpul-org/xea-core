from rest_framework import serializers

from .models import Address, Place


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('line1', 'line2')


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Place
        fields = ('url', 'name', 'owner', 'description', 'address')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.owner = validated_data.get('owner', instance.owner)
        instance.description = validated_data.get('nationality', instance.description)
        address_data = validated_data.get('address', instance.address)
        address = Address.objects.create(

            line1=address_data.get('line1',''),
            line2=address_data.get('line2','')
        )
        instance.address = address
        instance.save()
        return instance

    def create(self, validated_data):
        address_data = validated_data.get('address')
        address = Address.objects.create(
            line1=address_data.get('line1'),
            line2=address_data.get('line2')
        )
        address.save()
        place = Place.objects.create(
            name=validated_data.get('name'),
            owner=validated_data.get('owner'),
            description=validated_data.get('description'),
            address=address
        )

        place.save()
        return place
