from rest_framework import serializers

from .models import Address, Place


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('street_name', 'civic', 'floor', 'door', 'city', 'postal_code', 'region', 'nation')


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Place
        fields = ('url', 'name', 'owner', 'description', 'address')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.owner = validated_data.get('owner', instance.owner)
        instance.description = validated_data.get('nationality', instance.description)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance

    def create(self, validated_data):
        address_data = validated_data.get('address')
        address = Address.objects.create(street_name=address_data.get('street_name'),
                                         civic=address_data.get('civic'),
                                         floor=address_data.get('floor'),
                                         door=address_data.get('door'),
                                         city=address_data.get('city'),
                                         postal_code=address_data.get('postal_code'),
                                         region=address_data.get('region'),
                                         nation=address_data.get('nation')
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
