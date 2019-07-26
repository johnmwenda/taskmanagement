from django.test import TestCase

from tasksystem.departments.models import Department
from django.contrib.auth.models import User
# Create your tests here.

from tasksystem.accounts.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@gmail.com', password='password',
                                    first_name='test', last_name='last')
        self.user_no_initial_password = User.objects.create(email='test1@gmail.com', 
                                    first_name='test1', last_name='last1')
        
    def test_if_no_password_is_passed_a_default_one_is_created(self):
        self.assertNotEqual(self.user_no_initial_password.password,'')

    def test_string_representation_functions(self):
        self.assertEqual(self.user.__str__(), 'test@gmail.com')
        self.assertEqual(self.user.get_short_name(), 'test')
        self.assertEqual(self.user.get_full_name(), 'test last')
