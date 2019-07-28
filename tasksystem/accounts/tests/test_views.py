from django.test import TestCase
from django.shortcuts import reverse

from django.contrib.auth import get_user_model
User=get_user_model()

class UserSignInViewTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(email='test@gmail.com', password='password')

    def test_user_sign_in_successful(self):
        data = {
            'email':'test@gmail.com',
            'password':'password'
        }
        resp = self.client.post(reverse('login'), data=data, format='json') 
        self.assertEqual(resp.status_code, 200)
        self.assertIn('token', str(resp.data))

    def test_user_sign_out_successful(self):
        resp = self.client.get(reverse('logout'))
        self.assertEqual(resp.status_code, 204)

class UserSignupViewTest(TestCase):
    fixtures = ['tasksystem/fixtures/department.json',]

    @classmethod
    def setUpTestData(self):
        self.data = {
            'email':'test@gmail.com',
            'password':'password',
            'first_name':'test',
            'last_name':'last',
            'department_id':'1'
        }

    def test_user_sign_up_successful(self):
        resp = self.client.post(reverse('signup'), data=self.data, format='json')
        self.assertEqual(resp.status_code, 201)
    
    def test_user_sign_up_no_password(self):
        '''
        If no password is pass, the custom behavior is to generate a password for the user
        '''
        no_pass_data = self.data.copy()
        no_pass_data.pop('password')
        resp = self.client.post(reverse('signup'), data=no_pass_data, format='json')
        self.assertEqual(resp.status_code, 201)
        
    def test_validation_error_weak_invalid_password(self):
        '''
        If password does not pass validators tests, ensure the errors are shown
        '''
        pass
