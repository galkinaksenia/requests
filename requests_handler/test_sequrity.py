from django.test import TestCase
from django.urls import reverse
from .models import User

class RegisterViewTest(TestCase):
    def test_register_view(self):
        # Test case for successful registration
        response = self.client.post(reverse('register'), {'username': 'test_user', 'password1': 'test_password', 'password2': 'test_password'})
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'test_user')

        # Test case for invalid input
        response = self.client.post(reverse('register'), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

from django.test import TestCase
from django.urls import reverse
from .models import User

class UserListViewTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='test_user1', password='test_password')
        User.objects.create_user(username='test_user2', password='test_password')

    def test_user_list_view(self):
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 2)
        self.assertEqual(response.context['users'][0].username, 'test_user1')
        self.assertEqual(response.context['users'][1].username, 'test_user2')


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Device

User = get_user_model()

class AuthenticationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.device = Device.objects.create(user=self.user)

    def test_login(self):
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue('_auth_user_id' in self.client.session)  # Check if user is logged in

    def test_login_with_mfa(self):
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(response.url, reverse('otp_login'))  # Check if redirected to OTP login

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'wrong_password'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)  # Check if user is not logged in



