from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from core.tasks import send_verification_email

from core.storage_backends import ClubLogoStorage, RoomImageStorage, EventImageStorage
from django.utils.timezone import timezone, now
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Student(AbstractUser):
    faculty = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_email_verified = models.BooleanField(default=False)


class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='',
        storage=ClubLogoStorage(),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ClubMember(models.Model):
    class RoleChoices(models.TextChoices):
        MEMBER = 'member', 'Member'
        HEAD = 'head', 'Head'

    user = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=10, choices=RoleChoices.choices, default=RoleChoices.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'club')

    def __str__(self):
        return f"{self.user} in {self.club} as {self.role}"


class Room(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    location_description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='',
        storage=RoomImageStorage(),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.name} ({self.capacity} seats)"


class Event(models.Model):
    class TicketTypeChoices(models.TextChoices):
        FREE = 'free', 'Free'
        PAID = 'paid', 'Paid'

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name='events')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_tickets = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    image = models.ImageField(
        upload_to='',
        storage=EventImageStorage(),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ticket_type = models.CharField(max_length=10, choices=TicketTypeChoices.choices,
                                   default=TicketTypeChoices.FREE)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def tickets_sold(self):
        return self.tickets.count()

    @property
    def tickets_available(self):
        return self.total_tickets - self.tickets_sold


class Ticket(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'event')

    def __str__(self):
        return f"Ticket for {self.student} to {self.event}"


class Subscription(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subscriptions')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'club')

    def __str__(self):
        return f"{self.user} subscribes to {self.club}"


class EventReview(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='event_reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"Review by {self.user} on {self.event}: {self.rating}"


class EmailVerification(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        VERIFIED = 'Verified', 'Verified'
        EXPIRED = 'Expired', 'Expired'

    code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_index=True
    )
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(
        default=now() + timedelta(minutes=15)
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING
    )

    class Meta:
        unique_together = ('user', 'code')
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'

    def __str__(self):
        return f'Email Verification for {self.user.email}'

    @property
    def is_expired(self):
        return now() >= self.expiration

    @property
    def is_verified(self):
        return self.status == self.Status.VERIFIED

    def send_verification_email(self):
        send_verification_email.delay(self.user.username, self.code)

    def mark_as_verified(self):
        if not self.is_expired:
            self.status = self.Status.VERIFIED
            self.save(update_fields=['status'])

    def update_status(self):
        if self.is_expired and self.status != self.Status.EXPIRED:
            self.status = self.Status.EXPIRED
            self.save(update_fields=['status'])