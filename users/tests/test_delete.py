from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from rest_framework.authtoken.models import Token

from users.models import User

class UserDeleteTest(APITestCase):
    fixtures = ["user-fixture.json"]

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.get(is_superuser=True)
        cls.user       = User.objects.get(is_staff=False)

        cls.client = APIClient()
    
    def test_should_not__accept_non_admin_user(self):
        token,_ = Token.objects.get_or_create(user_id=self.user.id)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response      = self.client.delete(f"/api/users/{self.user.id}/", self.user_patch_info)
        response_dict = response.json()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)        
        self.assertIn('detail', response_dict.keys())

    def test_should_not_accept_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token 1234')

        response      = self.client.delete(f"/api/users/{self.user.id}/", self.user_patch_info)
        response_dict = response.json()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)        
        self.assertIn('detail', response_dict.keys())
    
    def test_should_delete_user(self):
        token,_ = Token.objects.get_or_create(user_id=self.admin_user.id)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.delete(f"/api/users/{self.user.id}/")
        
        try:
            User.objects.get(id=self.user.id)
        except:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

