from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from rest_framework.authtoken.models import Token

from users.models import User
from events.models import Event
from reviews.models import Review

class DeleteReviewTest(APITestCase):
    fixtures = ["user-fixture.json", "event-fixture.json", "review-fixture.json"]

    @classmethod
    def setUpTestData(cls):
        cls.event        = Event.objects.all()[0]
        cls.review       = Review.objects.filter(event_id=cls.event.id)[0]
        cls.other_review = Review.objects.filter(event_id=cls.event.id)[1]
        cls.admin_user   = User.objects.get(is_superuser=True)
        cls.owner_user   = User.objects.get(id=cls.review.user.id)
        cls.other_user   = User.objects.filter(id=cls.review.user.id, exclude=True)

        cls.client = APIClient()
    
    def test_should_not_accept_other_user(self):
        token,_ = Token.objects.get_or_create(user_id=self.other_user.id)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response      = self.client.delete(f"/api/events/{self.event.id}/reviews/{self.review.id}")
        response_dict = response.json()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)        
        self.assertIn('detail', response_dict.keys())


    def test_should_not_accept_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token 1234')

        response      = self.client.delete(f"/api/events/{self.event.id}/reviews/{self.review.id}")
        response_dict = response.json()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)        
        self.assertIn('detail', response_dict.keys())
    
    def test_should_delete_review_with_admin_token(self):
        token,_ = Token.objects.get_or_create(user_id=self.admin_user.id)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.delete(f"/api/events/{self.event.id}/lineup/{self.review.id}")
        
        try:
            Review.objects.get(id=self.event.id)
        except:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_should_delete_review_with_owner_token(self):
        token,_ = Token.objects.get_or_create(user_id=self.owner_user.id)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.delete(f"/api/events/{self.event.id}/reviews/{self.review.id}")
        
        try:
            Review.objects.get(id=self.event.id)
        except:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

