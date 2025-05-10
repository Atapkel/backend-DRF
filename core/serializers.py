from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model


class StudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Student
        fields = ['id', 'username', 'email', 'faculty', 'speciality',
                  'wallet_balance', 'password', 'password2']
        extra_kwargs = {
            'wallet_balance': {'read_only': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = Student.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            faculty=validated_data.get('faculty', ''),
            speciality=validated_data.get('speciality', '')
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)

        if password and password2:
            if password != password2:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ClubSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = ['id', 'name', 'description', 'image', 'created_at']
        read_only_fields = ['created_at']

    def validate_name(self, value):
        if Club.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError({"name": "A club with this name already exists."})
        return value

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None



class ClubMemberSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    club_name = serializers.ReadOnlyField(source='club.name')
    class Meta:
        model = ClubMember
        fields = ['id', 'user', 'username', 'club', 'club_name', 'role', 'joined_at']
        read_only_fields = ['joined_at']

    def validate(self, data):
        user = data.get('user')
        club = data.get('club')

        if self.instance is None and (not user or not club):
            raise serializers.ValidationError("Both user and club are required.")

        if self.instance is None and ClubMember.objects.filter(user=user, club=club).exists():
            raise serializers.ValidationError("This user is already a member of this club.")

        request = self.context.get('request')
        if data.get('role') == ClubMember.RoleChoices.HEAD and not request.user.is_staff:
            raise serializers.ValidationError("Only admin users can assign the HEAD role.")


class RoomSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity', 'location_description', 'image']

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class EventSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    club_name = serializers.ReadOnlyField(source='club.name')
    room_name = serializers.ReadOnlyField(source='room.name')
    tickets_available = serializers.ReadOnlyField()
    tickets_sold = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'club', 'club_name',
            'room', 'room_name', 'start_date', 'end_date',
            'ticket_price', 'total_tickets', 'image', 'created_at',
            'ticket_type', 'tickets_available', 'tickets_sold'
        ]
        read_only_fields = ['created_at', 'tickets_available', 'tickets_sold']

    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError(
                    {"end_date": "End date must be later than start date."}
                )

        if data.get('ticket_type') == Event.TicketTypeChoices.FREE and data.get('ticket_price', 0) > 0:
            raise serializers.ValidationError(
                {"ticket_price": "Free events should have a ticket price of 0."}
            )

        return data

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class TicketSerializer(serializers.ModelSerializer):
    student_username = serializers.ReadOnlyField(source='student.username')
    event_title = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = Ticket
        fields = ['id', 'student', 'student_username', 'event', 'event_title', 'purchased_at']
        read_only_fields = ['purchased_at']

    def validate(self, data):
        event = data.get('event')
        if event and event.tickets_available <= 0:
            raise serializers.ValidationError(
                {"event": "No tickets available for this event."}
            )

        student = data.get('student')
        if student and event and Ticket.objects.filter(student=student, event=event).exists():
            raise serializers.ValidationError(
                {"student": "This student already has a ticket for this event."}
            )

        if event and event.ticket_type == Event.TicketTypeChoices.PAID:
            if student.wallet_balance < event.ticket_price:
                raise serializers.ValidationError(
                    {"student": "Insufficient wallet balance to purchase this ticket."}
                )

        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    club_name = serializers.ReadOnlyField(source='club.name')

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'user_username', 'club', 'club_name', 'subscribed_at']
        read_only_fields = ['subscribed_at']

    def validate(self, data):
        user = data.get('user')
        club = data.get('club')

        if self.instance is None and Subscription.objects.filter(user=user, club=club).exists():
            raise serializers.ValidationError(
                {"user": "This user is already subscribed to this club."}
            )

        return data


class EventReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    event_title = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = EventReview
        fields = ['id', 'event', 'event_title', 'user', 'user_username', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at', 'user']

    # def validate(self, data):
    #     event = data.get('event')
    #
    #     if self.instance is None and EventReview.objects.filter(event=event, user=user).exists():
    #         raise serializers.ValidationError(
    #             {"user": "You have already reviewed this event."}
    #         )

        # if not Ticket.objects.filter(event=event, student=user).exists():
        #     raise serializers.ValidationError(
        #         {"user": "You can only review events you have tickets for."}
        #     )

        # return data
