from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import io
from PIL import Image

User = get_user_model()


class ProfileUpdateAPITestCase(TestCase):
    """Test cases for Profile Update API"""

    def setUp(self):
        """Set up test client and create test user"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            full_name='Test User',
            phone='+1234567890',
            gender='M',
            password='testpass123'
        )
        
        # Generate JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_partial_profile_update_success(self):
        """Test successful partial profile update"""
        url = '/api/auth/profile/update/'
        data = {
            'full_name': 'Updated Test User',
            'phone': '+9876543210'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Profile updated successfully.')
        self.assertEqual(response.data['user']['full_name'], 'Updated Test User')
        self.assertEqual(response.data['user']['phone'], '+9876543210')
        
        # Verify database update
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Test User')
        self.assertEqual(self.user.phone, '+9876543210')

    def test_full_profile_update_success(self):
        """Test successful full profile update"""
        url = '/api/auth/profile/update/'
        data = {
            'username': 'newusername',
            'full_name': 'New Full Name',
            'email': 'newemail@example.com',
            'phone': '+1111111111',
            'gender': 'F'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'newusername')
        self.assertEqual(response.data['user']['email'], 'newemail@example.com')

    def test_duplicate_username_validation(self):
        """Test that duplicate username is rejected"""
        # Create another user
        User.objects.create_user(
            email='other@example.com',
            username='otherusername',
            full_name='Other User',
            password='testpass123'
        )
        
        url = '/api/auth/profile/update/'
        data = {'username': 'otherusername'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_duplicate_email_validation(self):
        """Test that duplicate email is rejected"""
        # Create another user
        User.objects.create_user(
            email='other@example.com',
            username='otherusername',
            full_name='Other User',
            password='testpass123'
        )
        
        url = '/api/auth/profile/update/'
        data = {'email': 'other@example.com'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_profile_update_without_authentication(self):
        """Test that profile update requires authentication"""
        self.client.credentials()  # Remove authentication
        
        url = '/api/auth/profile/update/'
        data = {'full_name': 'Should Fail'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AvatarUpdateAPITestCase(TestCase):
    """Test cases for Avatar Update API"""

    def setUp(self):
        """Set up test client and create test user"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            full_name='Test User',
            phone='+1234567890',
            password='testpass123'
        )
        
        # Generate JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def create_test_image(self):
        """Create a test image file"""
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'JPEG')
        file.seek(0)
        return SimpleUploadedFile(
            'test_avatar.jpg',
            file.read(),
            content_type='image/jpeg'
        )

    def test_avatar_upload_success(self):
        """Test successful avatar upload"""
        url = '/api/auth/profile/avatar/'
        image = self.create_test_image()
        data = {'avatar': image}
        
        response = self.client.put(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Avatar updated successfully.')
        self.assertIsNotNone(response.data['user']['avatar'])
        
        # Verify database update
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar)

    def test_avatar_update_replaces_old(self):
        """Test that uploading new avatar replaces old one"""
        url = '/api/auth/profile/avatar/'
        
        # Upload first avatar
        image1 = self.create_test_image()
        self.client.put(url, {'avatar': image1}, format='multipart')
        
        self.user.refresh_from_db()
        old_avatar_name = self.user.avatar.name
        
        # Upload second avatar
        image2 = self.create_test_image()
        response = self.client.put(url, {'avatar': image2}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        new_avatar_name = self.user.avatar.name
        
        # Verify avatar was replaced
        self.assertNotEqual(old_avatar_name, new_avatar_name)

    def test_avatar_delete_success(self):
        """Test successful avatar deletion"""
        # First upload an avatar
        url = '/api/auth/profile/avatar/'
        image = self.create_test_image()
        self.client.put(url, {'avatar': image}, format='multipart')
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar)
        
        # Now delete it
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Avatar deleted successfully.')
        self.assertIsNone(response.data['user']['avatar'])
        
        # Verify database update
        self.user.refresh_from_db()
        self.assertFalse(self.user.avatar)

    def test_avatar_delete_when_no_avatar(self):
        """Test deleting avatar when user has no avatar"""
        url = '/api/auth/profile/avatar/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No avatar to delete.')

    def test_avatar_upload_invalid_file_type(self):
        """Test that invalid file types are rejected"""
        url = '/api/auth/profile/avatar/'
        
        # Create a text file instead of image
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'This is not an image',
            content_type='text/plain'
        )
        data = {'avatar': invalid_file}
        
        response = self.client.put(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('avatar', response.data)

    def test_avatar_upload_without_authentication(self):
        """Test that avatar upload requires authentication"""
        self.client.credentials()  # Remove authentication
        
        url = '/api/auth/profile/avatar/'
        image = self.create_test_image()
        data = {'avatar': image}
        
        response = self.client.put(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_avatar_patch_method(self):
        """Test that PATCH method works for avatar upload"""
        url = '/api/auth/profile/avatar/'
        image = self.create_test_image()
        data = {'avatar': image}
        
        response = self.client.patch(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['user']['avatar'])


class ProfileViewAPITestCase(TestCase):
    """Test cases for Profile View API (existing endpoint)"""

    def setUp(self):
        """Set up test client and create test user"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            full_name='Test User',
            phone='+1234567890',
            password='testpass123'
        )
        
        # Generate JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_get_profile_success(self):
        """Test successful profile retrieval"""
        url = '/api/auth/profile/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'testuser@example.com')
        self.assertEqual(response.data['full_name'], 'Test User')

    def test_get_profile_without_authentication(self):
        """Test that profile retrieval requires authentication"""
        self.client.credentials()  # Remove authentication
        
        url = '/api/auth/profile/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
