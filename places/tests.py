from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.tests import create_n_users
from .models import Place


class PlacesTest(APITestCase):
    # Default place data

    name = 'place'
    description = 'A very nice place'

    # Default address data

    street = 'streetname'
    civic = '123'
    floor = '10'
    door = 'c'
    city = 'La Coruña'
    postal_code = '15005'
    region = 'Galicia'
    nation = 'Spain'

    line1 = street + ' ' + civic + ' ' + floor + door
    line2 = postal_code + ' ' + city + ', ' + nation
    main_url = reverse('place-list')

    address_payload = {'line1': line1,
                       'line2': line2,
                       }

    place_payload = {'name': name,
                     'description': description,
                     'address': address_payload
                     }

    DEFAULT_USERS_NUMBER = 3
    DEFAULT_PLACES_NUMBER = 3

    def setUp(self):
        create_n_users(self.DEFAULT_USERS_NUMBER)

    def create_n_places(self, n):
        payload = self.place_payload
        for i in range(0, n):
            owner_url = reverse('user-detail', kwargs={'pk': n % self.DEFAULT_USERS_NUMBER + 1})
            payload.update({'owner': owner_url, 'name': self.name + str(n)})
            response = self.client.post(self.main_url, payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_place(self):
        payload = self.place_payload
        payload.update({'owner': reverse('user-detail', kwargs={'pk': 1})})
        response = self.client.post(self.main_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_n_places(self):
        self.create_n_places(self.DEFAULT_PLACES_NUMBER)
        queryset = Place.objects.all()
        self.assertEqual(len(queryset), self.DEFAULT_PLACES_NUMBER)

    def test_owner_updates_place(self):
        self.create_n_places(self.DEFAULT_PLACES_NUMBER)
        url = reverse('place-update-place-data', kwargs={'pk': 1})
        place = Place.objects.get(pk=1)
        owner = place.owner
        self.client.force_login(owner)
        new_place_name = 'newname'
        response = self.client.patch(path=url, data={'name': new_place_name}, format='json')
        place = Place.objects.get(pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(place.name, new_place_name)

    def test_anonym_updates_place(self):
        self.create_n_places(self.DEFAULT_PLACES_NUMBER)
        new_place_name = 'newname'
        url = reverse('place-update-place-data', kwargs={'pk': 1})
        response = self.client.patch(path=url, data={'name': new_place_name})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def logged_user_updates_not_owned_place(self):
        self.create_n_places(self.DEFAULT_PLACES_NUMBER)
        url = reverse('place-update-place-data', kwargs={'pk': 1})
        owner = get_user_model().objects.get(pk=2)
        self.client.force_login(owner)
        new_place_name = 'newname'
        response = self.client.patch(path=url, data={'name': new_place_name}, format='json')
        place = Place.objects.get(pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_place_address(self):
        self.create_n_places(self.DEFAULT_PLACES_NUMBER)
        url = reverse('place-update-place-data', kwargs={'pk': 1})
        place = Place.objects.get(pk=1)
        owner = place.owner
        self.client.force_login(owner)
        line1 = 'newstreetname 5b'
        address_payload = {'line1': line1}
        response = self.client.patch(path=url, data={'address': address_payload}, format='json')
        place = Place.objects.get(pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(place.address.line1, line1)
