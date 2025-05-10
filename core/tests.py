from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Student, Club
# Using Student directly as it's the user model.

class StudentAPITests(APITestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = Student.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpassword',
            faculty=Student.FacultyChoices.FEENS, # Ensure all required fields are provided
            speciality='Administration'
        )
        # Data payload for creating a new student
        self.student_data_payload = {
            'username': 'teststudent',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password2': 'testpassword123',
            'faculty': Student.FacultyChoices.FEENS,
            'speciality': 'Computer Science'
        }
        # Create a regular student user
        self.regular_student = Student.objects.create_user(
            username='regularuser', 
            email='regular@example.com', 
            password='regularpassword',
            faculty=Student.FacultyChoices.EDU,
            speciality='History'
        )

    # Endpoint: /students/
    # View: StudentListCreateView
    # Methods: POST (Create), GET (List)

    def test_post_create_student(self):
        """
        Test POST /students/ to create a new student.
        View: StudentListCreateView. Permissions: AllowAny (for POST).
        """
        url = reverse('student-list')
        response = self.client.post(url, self.student_data_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Initial (admin, regular_student) + 1 new student
        self.assertEqual(Student.objects.count(), 3) 
        self.assertEqual(response.data['username'], self.student_data_payload['username'])
        self.assertNotIn('password', response.data) # Password should not be in response
        self.assertNotIn('password2', response.data)

    def test_get_list_students_as_admin(self):
        """
        Test GET /students/ to list students (as admin).
        View: StudentListCreateView. Permissions: IsAdminOrHeadOfThisClub (for GET) - testing with admin.
        """
        url = reverse('student-list')
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response data is a list and contains expected number of users (or more if paginated)
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) >= 2) # admin_user and regular_student

    # Endpoint: /students/<pk>/
    # View: StudentDetailAPIView
    # Methods: GET (Retrieve), PUT (Update), DELETE (Destroy)
    # Permissions: IsAuthenticated, IsAdminUser

    def test_get_retrieve_student_as_admin(self):
        """
        Test GET /students/<pk>/ to retrieve a specific student (as admin).
        View: StudentDetailAPIView.
        """
        url = reverse('student-detail', kwargs={'pk': self.regular_student.pk})
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.regular_student.username)

    def test_put_update_student_as_admin(self):
        """
        Test PUT /students/<pk>/ to update a specific student (as admin).
        View: StudentDetailAPIView.
        """
        url = reverse('student-detail', kwargs={'pk': self.regular_student.pk})
        self.client.force_authenticate(user=self.admin_user)
        updated_data = {
            'username': 'updated_regular_user',
            'email': self.regular_student.email,  # Keep email same or ensure uniqueness
            'faculty': Student.FacultyChoices.LAW,
            'speciality': 'Corporate Law',
            'password': 'newpassword123',  # Add password
            'password2': 'newpassword123'  # Add password2
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_student.refresh_from_db()
        self.assertEqual(self.regular_student.username, updated_data['username'])
        self.assertEqual(self.regular_student.faculty, updated_data['faculty'])

    def test_delete_student_as_admin(self):
        """
        Test DELETE /students/<pk>/ to delete a specific student (as admin).
        View: StudentDetailAPIView.
        """
        student_to_delete = Student.objects.create_user(
            username='user_to_delete', password='password123',
            faculty=Student.FacultyChoices.BS, speciality='Economics'
        )
        initial_student_count = Student.objects.count()
        url = reverse('student-detail', kwargs={'pk': student_to_delete.pk})
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Student.objects.count(), initial_student_count - 1)
        self.assertFalse(Student.objects.filter(pk=student_to_delete.pk).exists())

    # Endpoint: /students/current/
    # View: CurrentStudentView
    # Methods: GET (Retrieve)
    # Permissions: IsAuthenticated

    def test_get_current_student_authenticated(self):
        """
        Test GET /students/current/ to retrieve current authenticated student's details.
        View: CurrentStudentView.
        """
        url = reverse('current-student')
        self.client.force_authenticate(user=self.regular_student)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.regular_student.username)
        self.assertEqual(response.data['id'], self.regular_student.id)


class ClubAPITests(APITestCase):
    def setUp(self):
        self.admin_user = Student.objects.create_superuser(
            username='clubadmin', email='clubadmin@example.com', password='adminpassword'
        )
        # Data payload for creating a new club
        self.club_data_payload = {
            'name': 'The Coding Club',
            'description': 'A club for passionate coders.'
        }
        # Create an existing club for detail view tests
        self.existing_club = Club.objects.create(name='Pioneer Club', description='The first club on campus.')

    # Endpoint: /clubs/
    # View: ClubListCreateView
    # Methods: POST (Create), GET (List)

    def test_post_create_club_as_admin(self):
        """
        Test POST /clubs/ to create a new club (as admin).
        View: ClubListCreateView. Permissions: IsAdminUser (for POST).
        """
        url = reverse('club-list')
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, self.club_data_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Initial (existing_club) + 1 new club
        self.assertEqual(Club.objects.count(), 2) 
        self.assertEqual(response.data['name'], self.club_data_payload['name'])

    def test_get_list_clubs(self):
        """
        Test GET /clubs/ to list all clubs.
        View: ClubListCreateView. Permissions: AllowAny (for GET).
        """
        # Create another club to test listing multiple items
        Club.objects.create(name="Debate Society", description="For sharp minds.")
        url = reverse('club-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2) # existing_club + Debate Society

    # Endpoint: /clubs/<pk>/
    # View: ClubDetailAPIView
    # Methods: GET (Retrieve), PUT (Update), DELETE (Destroy)

    def test_get_retrieve_club(self):
        """
        Test GET /clubs/<pk>/ to retrieve a specific club.
        View: ClubDetailAPIView. Permissions: AllowAny (for GET).
        """
        url = reverse('club-detail', kwargs={'pk': self.existing_club.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.existing_club.name)

    def test_put_update_club_as_admin(self):
        """
        Test PUT /clubs/<pk>/ to update a specific club (as admin).
        View: ClubDetailAPIView. Permissions: IsAdminUser (for PUT).
        """
        url = reverse('club-detail', kwargs={'pk': self.existing_club.pk})
        self.client.force_authenticate(user=self.admin_user)
        updated_data = {
            'name': 'Pioneer Club (Renamed)', 
            'description': 'The first club, now with an updated description.'
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_club.refresh_from_db()
        self.assertEqual(self.existing_club.name, updated_data['name'])
        self.assertEqual(self.existing_club.description, updated_data['description'])

    def test_delete_club_as_admin(self):
        """
        Test DELETE /clubs/<pk>/ to delete a specific club (as admin).
        View: ClubDetailAPIView. Permissions: IsAdminUser (for DELETE).
        """
        club_to_delete = Club.objects.create(name='Temporary Club', description='This club will be deleted.')
        initial_club_count = Club.objects.count()
        url = reverse('club-detail', kwargs={'pk': club_to_delete.pk})
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Club.objects.count(), initial_club_count - 1)
        self.assertFalse(Club.objects.filter(pk=club_to_delete.pk).exists())

