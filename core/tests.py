from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from django.utils import timezone
import datetime
from django.contrib.auth import get_user_model

from .models import (
    Student, Club, ClubMember, Room, Event,
    Ticket, Subscription, EventReview
)


class StudentTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = Student.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            faculty=Student.FacultyChoices.FEENS,
            speciality='Admin'
        )

        # Create regular student
        self.student = Student.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='student123',
            faculty=Student.FacultyChoices.BS,
            speciality='Computer Science',
            wallet_balance=Decimal('100.00')
        )

        self.client = APIClient()

    def test_create_student(self):
        """Test creating a new student"""
        url = reverse('student-list')
        data = {
            'username': 'newstudent',
            'email': 'newstudent@example.com',
            'password': 'newstudent123',
            'password2': 'newstudent123',
            'faculty': Student.FacultyChoices.LAW,
            'speciality': 'Criminal Law'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 3)
        self.assertEqual(Student.objects.get(username='newstudent').speciality, 'Criminal Law')

    def test_password_mismatch(self):
        """Test password validation"""
        url = reverse('student-list')
        data = {
            'username': 'mismatch',
            'email': 'mismatch@example.com',
            'password': 'password123',
            'password2': 'different123',
            'faculty': Student.FacultyChoices.LAW,
            'speciality': 'Law'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_students_list_as_admin(self):
        """Test that admin can get all students"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # admin + student1

    def test_get_current_student(self):
        """Test that a student can get their own profile"""
        self.client.force_authenticate(user=self.student)
        url = reverse('current-student')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'student1')
        self.assertEqual(response.data['wallet_balance'], '100.00')

    def test_update_student(self):
        """Test updating a student"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student-detail', kwargs={'pk': self.student.id})
        data = {
            'speciality': 'Data Science',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.speciality, 'Data Science')


class ClubTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = Student.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        # Create regular student
        self.student = Student.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='student123'
        )

        # Create a club
        self.club = Club.objects.create(
            name='Tech Club',
            description='A club for tech enthusiasts'
        )

        # Create club membership
        self.membership = ClubMember.objects.create(
            user=self.student,
            club=self.club,
            role=ClubMember.RoleChoices.MEMBER
        )

        self.client = APIClient()

    def test_create_club_as_admin(self):
        """Test that admin can create a club"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('club-list')
        data = {
            'name': 'Chess Club',
            'description': 'A club for chess players'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Club.objects.count(), 2)

    def test_create_club_as_student_fails(self):
        """Test that a regular student cannot create a club"""
        self.client.force_authenticate(user=self.student)
        url = reverse('club-list')
        data = {
            'name': 'Chess Club',
            'description': 'A club for chess players'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_clubs_as_student(self):
        """Test that a student can get the list of clubs"""
        self.client.force_authenticate(user=self.student)
        url = reverse('club-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_club_as_admin(self):
        """Test that admin can update a club"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('club-detail', kwargs={'pk': self.club.id})
        data = {
            'description': 'Updated description'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, 'Updated description')

    def test_club_name_unique(self):
        """Test that club names must be unique"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('club-list')
        data = {
            'name': 'Tech Club',  # Same name as existing club
            'description': 'Another tech club'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ClubMembershipTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = Student.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        # Create regular students
        self.student1 = Student.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='student123'
        )

        self.student2 = Student.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='student123'
        )

        # Create a club
        self.club = Club.objects.create(
            name='Tech Club',
            description='A club for tech enthusiasts'
        )

        # Create club membership
        self.membership = ClubMember.objects.create(
            user=self.student1,
            club=self.club,
            role=ClubMember.RoleChoices.HEAD
        )

        self.client = APIClient()

    def test_add_member_as_head(self):
        """Test that a club head can add members"""
        self.client.force_authenticate(user=self.student1)
        url = reverse('club-members', kwargs={'club_pk': self.club.id})
        data = {
            'user': self.student2.id,
            'role': ClubMember.RoleChoices.MEMBER
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClubMember.objects.count(), 2)

    def test_add_member_duplicate_fails(self):
        """Test that a student cannot be added to a club twice"""
        self.client.force_authenticate(user=self.student1)
        url = reverse('club-members', kwargs={'club_pk': self.club.id})
        data = {
            'user': self.student1.id,  # Already a member
            'role': ClubMember.RoleChoices.MEMBER
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_head_as_admin(self):
        """Test that admin can assign a club head"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('club-head-assign', kwargs={'club_pk': self.club.id, 'user_pk': self.student2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        membership = ClubMember.objects.get(user=self.student2, club=self.club)
        self.assertEqual(membership.role, ClubMember.RoleChoices.HEAD)

    def test_get_user_clubs(self):
        """Test getting clubs a user is a member of"""
        self.client.force_authenticate(user=self.student1)
        url = reverse('user-clubs', kwargs={'user_pk': self.student1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['club_name'], 'Tech Club')


class RoomTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = Student.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        # Create regular student
        self.student = Student.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='student123'
        )

        # Create a room
        self.room = Room.objects.create(
            name='Conference Hall A',
            capacity=100,
            location_description='Main building, 2nd floor'
        )

        self.client = APIClient()

    def test_create_room_as_admin(self):
        """Test that admin can create a room"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('room-list')
        data = {
            'name': 'Seminar Room B',
            'capacity': 30,
            'location_description': 'Library building, 1st floor'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 2)

    def test_create_room_as_student_fails(self):
        """Test that a regular student cannot create a room"""
        self.client.force_authenticate(user=self.student)
        url = reverse('room-list')
        data = {
            'name': 'Seminar Room B',
            'capacity': 30,
            'location_description': 'Library building, 1st floor'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_rooms_as_student(self):
        """Test that a student can get the list of rooms"""
        self.client.force_authenticate(user=self.student)
        url = reverse('room-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_room_as_admin(self):
        """Test that admin can update a room"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('room-detail', kwargs={'pk': self.room.id})
        data = {
            'capacity': 120
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertEqual(self.room.capacity, 120)


class EventTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = Student.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        # Create regular students
        self.student1 = Student.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='student123',
            wallet_balance=Decimal('100.00')
        )

        self.student2 = Student.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='student123',
            wallet_balance=Decimal('50.00')
        )

        # Create a club
        self.club = Club.objects.create(
            name='Tech Club',
            description='A club for tech enthusiasts'
        )

        # Make student1 a club head
        self.membership = ClubMember.objects.create(
            user=self.student1,
            club=self.club,
            role=ClubMember.RoleChoices.HEAD
        )

        # Create room
        self.room = Room.objects.create(
            name='Conference Hall A',
            capacity=100,
            location_description='Main building, 2nd floor'
        )

        # Create event
        now = timezone.now()
        self.event = Event.objects.create(
            title='Tech Talk',
            description='A talk about emerging technologies',
            club=self.club,
            room=self.room,
            start_date=now + datetime.timedelta(days=1),
            end_date=now + datetime.timedelta(days=1, hours=2),
            ticket_price=Decimal('10.00'),
            total_tickets=50,
            ticket_type=Event.TicketTypeChoices.PAID
        )

        self.client = APIClient()

    def test_create_event_as_club_head(self):
        """Test that a club head can create an event"""
        self.client.force_authenticate(user=self.student1)
        url = reverse('club-events', kwargs={'club_pk': self.club.id})
        now = timezone.now()
        data = {
            'title': 'Coding Workshop',
            'description': 'Learn how to code',
            'room': self.room.id,
            'start_date': (now + datetime.timedelta(days=2)).isoformat(),
            'end_date': (now + datetime.timedelta(days=2, hours=3)).isoformat(),
            'ticket_price': '5.00',
            'total_tickets': 30,
            'ticket_type': Event.TicketTypeChoices.PAID
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)

    def test_get_upcoming_events(self):
        """Test filtering events by upcoming status"""
        self.client.force_authenticate(user=self.student2)
        url = reverse('event-list') + '?upcoming=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_event_as_club_head(self):
        """Test that a club head can update an event"""
        self.client.force_authenticate(user=self.student1)
        url = reverse('event-detail', kwargs={'pk': self.event.id})
        data = {
            'title': 'Updated Tech Talk',
            'ticket_price': '15.00'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Tech Talk')
        self.assertEqual(self.event.ticket_price, Decimal('15.00'))

    def test_free_event_validation(self):
        """Test validation for free events"""
        self.client.force_authenticate(user=self.student1)
        url = reverse('club-events', kwargs={'club_pk': self.club.id})
        now = timezone.now()
        data = {
            'title': 'Free Workshop',
            'description': 'Learn for free',
            'room': self.room.id,
            'start_date': (now + datetime.timedelta(days=2)).isoformat(),
            'end_date': (now + datetime.timedelta(days=2, hours=3)).isoformat(),
            'ticket_price': '5.00',  # Non-zero price for free event
            'total_tickets': 30,
            'ticket_type': Event.TicketTypeChoices.FREE
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TicketTests(APITestCase):
    def setUp(self):
        # Create regular students
        self.student1 = Student.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='student123',
            wallet_balance=Decimal('100.00')
        )

        self.student2 = Student.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='student123',
            wallet_balance=Decimal('50.00')
        )

        # Create a club
        self.club = Club.objects.create(
            name='Tech Club',
            description='A club for tech enthusiasts'
        )

        # Make student1 a club head
        self.membership = ClubMember.objects.create(
            user=self.student1,
            club=self.club,
            role=ClubMember.RoleChoices.HEAD
        )

        # Create room
        self.room = Room.objects.create(
            name='Conference Hall A',
            capacity=100,
            location_description='Main building, 2nd floor'
        )

        # Create events
        now = timezone.now()
        self.paid_event = Event.objects.create(
            title='Tech Talk',
            description='A talk about emerging technologies',
            club=self.club,
            room=self.room,
            start_date=now + datetime.timedelta(days=1),
            end_date=now + datetime.timedelta(days=1, hours=2),
            ticket_price=Decimal('10.00'),
            total_tickets=50,
            ticket_type=Event.TicketTypeChoices.PAID
        )

        self.free_event = Event.objects.create(
            title='Open House',
            description='Come see what we do',
            club=self.club,
            room=self.room,
            start_date=now + datetime.timedelta(days=2),
            end_date=now + datetime.timedelta(days=2, hours=2),
            ticket_price=Decimal('0.00'),
            total_tickets=100,
            ticket_type=Event.TicketTypeChoices.FREE
        )

        self.client = APIClient()

    def test_purchase_paid_ticket(self):
        """Test purchasing a ticket for a paid event"""
        self.client.force_authenticate(user=self.student2)
        url = reverse('event-tickets', kwargs={'event_pk': self.paid_event.id})
        initial_balance = self.student2.wallet_balance

        data = {
            'event': self.paid_event.id,
            'student': self.student2.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that wallet balance was decreased
        self.student2.refresh_from_db()
        self.assertEqual(self.student2.wallet_balance, initial_balance - self.paid_event.ticket_price)

        # Check that ticket was created
        self.assertEqual(Ticket.objects.filter(student=self.student2, event=self.paid_event).count(), 1)

    def test_purchase_free_ticket(self):
        """Test purchasing a ticket for a free event"""
        self.client.force_authenticate(user=self.student2)
        url = reverse('event-tickets', kwargs={'event_pk': self.free_event.id})
        initial_balance = self.student2.wallet_balance

        data = {
            'event': self.free_event.id,
            'student': self.student2.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that wallet balance was not changed
        self.student2.refresh_from_db()
        self.assertEqual(self.student2.wallet_balance, initial_balance)

        # Check that ticket was created
        self.assertEqual(Ticket.objects.filter(student=self.student2, event=self.free_event).count(), 1)

    def test_duplicate_ticket_purchase_fails(self):
        """Test that a student cannot buy two tickets for the same event"""
        # First purchase
        self.client.force_authenticate(user=self.student2)
        url = reverse('event-tickets', kwargs={'event_pk': self.free_event.id})
        data = {
            'event': self.free_event.id,
            'student': self.student2.id
        }
        self.client.post(url, data, format='json')

        # Second purchase attempt
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_insufficient_balance_fails(self):
        """Test that a student cannot buy a ticket if they don't have enough money"""
        # Set wallet balance to less than ticket price
        self.student2.wallet_balance = Decimal('5.00')
        self.student2.save()

        self.client.force_authenticate(user=self.student2)
        url = reverse('event-tickets', kwargs={'event_pk': self.paid_event.id})
        data = {
            'event': self.paid_event.id,
            'student': self.student2.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_ticket_refund(self):
        """Test canceling a ticket and getting a refund"""
        # Purchase ticket
        self.client.force_authenticate(user=self.student2)
        url = reverse('event-tickets', kwargs={'event_pk': self.paid_event.id})
        data = {
            'event': self.paid_event.id,
            'student': self.student2.id
        }
        response = self.client.post(url, data, format='json')
        ticket_id = response.data['id']

        # Check balance after purchase
        self.student2.refresh_from_db()
        balance_after_purchase = self.student2.wallet_balance

        # Cancel ticket
        url = reverse('ticket-detail', kwargs={'pk': ticket_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that balance was refunded
        self.student2.refresh_from_db()
        self.assertEqual(self.student2.wallet_balance, balance_after_purchase + self.paid_event.ticket_price)

        # Check that ticket was deleted
        self.assertEqual(Ticket.objects.filter(id=ticket_id).count(), 0)


class SubscriptionTests(APITestCase):
    def setUp(self):
        # Create regular students
        self.student1 = Student.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='student123'
        )

        self.student2 = Student.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='student123'
        )

        # Create clubs
        self.club1 = Club.objects.create(
            name='Tech Club',
            description='A club for tech enthusiasts'
        )

        self.club2 = Club.objects.create(
            name='Art Club',
            description='A club for art enthusiasts'
        )

        self.client = APIClient()

    def test_subscribe_to_club(self):
        """Test subscribing to a club"""
        self.client.force_authenticate(user=self.student1)
        url = reverse('club-subscriptions', kwargs={'club_pk': self.club1.id})
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertTrue(Subscription.objects.filter(user=self.student1, club=self.club1).exists())

    def test_duplicate_subscription_fails(self):
        """Test that a student cannot subscribe to the same club twice"""
        # First subscription
        self.client.force_authenticate(user=self.student1)
        url = reverse('club-subscriptions', kwargs={'club_pk': self.club1.id})
        self.client.post(url, {}, format='json')

        # Second subscription attempt
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_subscriptions(self):
        """Test getting all subscriptions for a user"""
        # Create subscriptions
        Subscription.objects.create(user=self.student1, club=self.club1)
        Subscription.objects.create(user=self.student1, club=self.club2)

        self.client.force_authenticate(user=self.student1)
        url = reverse('user-subscriptions', kwargs={'user_pk': self.student1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unsubscribe_from_club(self):
        """Test unsubscribing from a club"""
        # Create subscription
        subscription = Subscription.objects.create(user=self.student1, club=self.club1)

        self.client.force_authenticate(user=self.student1)
        url = reverse('subscription-detail', kwargs={'pk': subscription.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subscription.objects.count(), 0)
