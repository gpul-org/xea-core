
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import UserProfile

# Default test user data
username = 'user'
first_name = 'Firstname'
last_name = 'Lastname'
email = 'user@mydomain.com'
password = 'user123'

# Urls we are working with
registration_url = reverse('user-list')

DEFAULT_NUMBER_OF_CLIENTS_FOR_TESTS = 3


def get_default_user():
    user = User(username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email)
    return user


def get_n_users(n):
    """
    This generates n users with their data
    :param n: The number of users we want to create
    :return:
    """
    user = []
    for i in range(1, n + 1):
        myusername = username + str(i)
        myfirst_name = first_name + str(i)
        mylast_name = last_name + str(i)
        myemail = 'user' + str(i) + '@mydomain.com'
        mypassword = password
        newuser = User(username=myusername,
                       password=mypassword,
                       first_name=myfirst_name,
                       last_name=mylast_name,
                       email=myemail)
        user.append(newuser)
    return user


def find_between(string, substring1, substring2):
    try:
        start = string.index(substring1) + len(substring1)
        end = string.index(substring2, start)
        return string[start:end]
    except ValueError:
        return ""


def get_userid_from_url(url):
    """
    This function is user id to obtain the user id from the url provided by the API"
    """

    return find_between(url, 'users/', '/')


def create_n_users(n):
    username_base = 'user'
    for i in range(0, n):
        user = get_user_model().objects.create(username=username_base + str(i))


def get_signup_payload_from_user(user):
    """
    This function builds the payload used for registration requests from the user's data
    :param user:
    :return:
    """

    profile_payload = {'gender': '',
                       'birthdate': '',
                       'nationality': '',
                       'location': ''}

    payload = {'username': user.username,
               'first_name': user.first_name,
               'last_name': user.last_name,
               'email': user.email,
               'password': user.password,
               'profile': profile_payload
               }

    return payload


def get_activation_url_from_email(email):
    """
    here we parse the activation email to get the activation URL
    :param email: the activation email
    :return: The URL we parsed
    """
    url = "http" + email.body.split("http", 1)[1]
    return url


class RegistrationTest(APITestCase):
    def register_user(self):
        """
        A simple function used to register a new user by sending a POST to the registration endpoint
        :return: The id (pk) of the newly registered user
        """
        id = self.register_n_users(1)[0]
        return id

    def register_n_users(self, n):
        user = get_n_users(n)
        user_url = []
        for i in range(0, n):
            response = self.client.post(registration_url, get_signup_payload_from_user(user[i]), format='json')
            self.assertEquals(response.status_code, status.HTTP_201_CREATED)
            user_url.append(response.data['url'])
        return user_url

    def get_activation_email(self):
        """
        This function retrieves the activation mail from the mailbox
        :return:            """
        self.assertEquals(len(mail.outbox), 1)
        activation_email = mail.outbox[0]
        return activation_email

    def get_n_activation_mails(self, n):
        self.assertEquals(len(mail.outbox), n)
        return mail.outbox

    def test_register_user(self):
        """
        In this test we verify that after a new user is registered we can find him by querying the database
        We also verify that his "is_active" flag is set to False (he needs to activate trough the email yet)
        :return:
        """
        url = self.register_n_users(1)[0]
        uid = get_userid_from_url(url)
        queryset = User.objects.all().filter(pk=uid)
        self.assertTrue(queryset.exists())
        user = queryset[0]
        self.assertFalse(user.is_active)
        return uid

    def test_activate_user(self):
        """
        Here we verify that a user can be activated through a request to the URL we provide
        :return:
        """
        self.register_user()
        activation_email = self.get_activation_email()
        url = get_activation_url_from_email(activation_email)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reusing_activation_link(self):
        """
        If a client tries to access the activation URL but the user is already active the response should be a HTTP 403
        :return:
        """
        self.register_user()
        activation_email = self.get_activation_email()
        url = get_activation_url_from_email(activation_email)
        response1 = self.client.get(url)
        self.assertEquals(response1.status_code, status.HTTP_204_NO_CONTENT)
        response2 = self.client.get(url)
        self.assertEquals(response2.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_existing_entry_activation_link(self):
        """
        Here we prove that we forbid the access to a URL that is not associated with a registered user
        :return:
        """
        self.register_user()
        url = reverse('activation', kwargs={'upk': 8,
                                            'token': '4eh-xxxxxxxxxxxxxxxx'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_valid_token(self):
        """
        Similar to the previous one, now we will try to use a valid uidb64 with a not valid token
        :return:
        """
        url = self.register_user()
        upk = get_userid_from_url(url)
        url = reverse('activation', kwargs={'upk': upk, 'token': '4eh-xxxxxxxxxxxxxxxx'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_n_clients_activation_reverse_order(self):
        """
        in this test we register multiple clients and activate them in reverse order to prove that using an activation
        link doesn't invalidate another one
        :return:
        """
        self.register_n_users(DEFAULT_NUMBER_OF_CLIENTS_FOR_TESTS)
        mails = self.get_n_activation_mails(DEFAULT_NUMBER_OF_CLIENTS_FOR_TESTS)
        for i in range(DEFAULT_NUMBER_OF_CLIENTS_FOR_TESTS - 1, -1, -1):
            activation_url = get_activation_url_from_email(mails[i])
            response = self.client.get(activation_url)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)


class ChangePasswordTest(APITestCase):
    def setUp(self):
        create_n_users(DEFAULT_NUMBER_OF_CLIENTS_FOR_TESTS)

    def get_change_password_detail_url(self, pk):
        url = reverse('user-change-password', kwargs={'pk': pk})
        return url

    def test_user_changes_his_password(self):
        """
        In this scenario the user tries to update his password. We also prove that a GET request to the url will result
        in a 405 response (we only allow POST)
        :return:
        """
        user = get_user_model().objects.get(pk=1)
        self.client.force_login(user)
        url = self.get_change_password_detail_url(1)
        response1 = self.client.get(url)
        self.assertEquals(response1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response2 = self.client.post(url, {'password': 'newpassword'})
        self.assertEquals(response2.status_code, status.HTTP_200_OK)

    def test_admin_changes_user_password(self):
        """
        Here we verify that also a staff user can modify the user's password
        :return:
        """
        url = self.get_change_password_detail_url(1)
        admin = User.objects.create_superuser('admin', 'admin@domain.test', 'password')
        self.client.force_login(admin)
        response = self.client.post(url, {'password': 'newpassword'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_user_changes_other_account_password(self):
        """
        Here a user tries to change someone else's password
        :return:
        """
        url = self.get_change_password_detail_url(1)
        user = get_user_model().objects.get(pk=2)
        self.client.force_login(user)
        response = self.client.post(url, {'password': 'newpassword'})
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_changes_password(self):
        """
        Here an unauthenticated user tries to change someone's password
        :return:
        """
        url = self.get_change_password_detail_url(1)
        response = self.client.post(url, {'password': 'newpassword'})
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTest(APITestCase):
    default_test_payload = {"gender": "M", "nationality": "Argosdfdegfsey", "location": "palermo"}

    def setUp(self):
        create_n_users(DEFAULT_NUMBER_OF_CLIENTS_FOR_TESTS)

    def test_profile_creation(self):
        """
        Here we verify that creating a new user we automatically generate for him a new user profile
        :return:
        """
        queryset = UserProfile.objects.all()
        self.assertEquals(len(queryset), DEFAULT_NUMBER_OF_CLIENTS_FOR_TESTS)

    def test_profile_updated_by_owner(self):
        queryset = User.objects.all()
        user = queryset[0]
        self.client.force_login(user)
        url = reverse('user-update-profile', kwargs={'pk': user.pk})
        response = self.client.put(path=url, data=self.default_test_payload)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        profile = UserProfile.objects.get(pk=user.pk)
        self.assertEquals(profile.gender, self.default_test_payload.get('gender'))

    def test_profile_updated_by_staff(self):
        """
        Here we prove that a superuser can modify anyone else's profile
        :return:
        """
        admin = User.objects.create_superuser('admin', 'admin@domain.test', 'password')
        self.client.force_login(admin)
        url = reverse('user-update-profile', kwargs={'pk': 1})
        response = self.client.put(path=url, data=self.default_test_payload)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_profile_updated_by_another_logged_user(self):
        """
        Here a logged user tries to modify someone else's profile. The  server answers with a 403
        :return:
        """

        user = get_user_model().objects.get(pk=2)
        self.client.force_login(user)
        url = reverse('user-update-profile', kwargs={'pk': 1})
        response = self.client.put(path=url, data=self.default_test_payload)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_updated_by_guest(self):
        url = reverse('user-update-profile', kwargs={'pk': 1})
        response = self.client.put(path=url, data=self.default_test_payload)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile(self):
        user = get_user_model().objects.get(pk=1)
        self.client.force_login(user)
        url = reverse('user-detail', kwargs={'pk': user.pk})
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue('profile' in response.data)

    def test_profile_update_after_password_change(self):
        user = get_user_model().objects.get(pk=1)
        change_password_url = reverse('user-change-password', kwargs={'pk': user.pk})
        profile_url = reverse('user-update-profile', kwargs={'pk': user.pk})
        self.client.force_login(user)
        response1 = self.client.put(path=profile_url, data=self.default_test_payload)
        self.assertEquals(response1.status_code, status.HTTP_200_OK)
        response2 = self.client.post(path=change_password_url, data={'password': 'password2'})
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        response3 = self.client.put(path=profile_url, data=self.default_test_payload)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

