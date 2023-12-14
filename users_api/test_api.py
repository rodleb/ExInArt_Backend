import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xnart.settings")
import django
django.setup()


from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
import pytest

User = get_user_model()

@pytest.mark.django_db
class RegisterUserAPITest(TestCase):
    def test_register_user(self):
        # Define test data
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'first_name': 'Test',
            'last_name': 'User',
        }

        # Get the URL for the 'register_user' view
        url = reverse('register')

        # Make a POST request to the URL with the test data
        response = self.client.post(url, data, format='json')

        # Print the response status code and content
        print(response.status_code)
        print(response.content)

        # Check that the response status code is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that a user is created in the database
        self.assertTrue(User.objects.filter(username='testuser').exists())

        # Deserialize the response content to a Python dictionary
        response_data = response.json()

        # Check that the response contains the expected keys
        expected_keys = [
            'access_token',
            'refresh_token',
            'verification_link',
            'user_email',
            'first_name',
            'last_name',
            'user_id',
            'username',
        ]
        for key in expected_keys:
            self.assertIn(key, response_data)

        # Check that an email with the verification link is sent
        # self.assertEqual(len(mail.outbox), 1)
        # verification_link = mail.outbox[0].body
        # self.assertIn('User created successfully.', verification_link)
