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
    class Meta:
        model = Club
        fields = ['id', 'name', 'description', 'image', 'created_at']
        read_only_fields = ['created_at']

    def validate_name(self, value):
        if Club.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError({"name": "A club with this name already exists."})
        return value




class ClubMemberSerializer(serializers.ModelSerializer):
    user = StudentSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        write_only=True,
        source='user'
    )
    club = ClubSerializer(read_only=True)
    club_id = serializers.PrimaryKeyRelatedField(
        queryset=Club.objects.all(),
        write_only=True,
        source='club'
    )

    class Meta:
        model = ClubMember
        fields = ['id', 'user', 'user_id', 'club', 'club_id', 'role', 'joined_at']
        read_only_fields = ['joined_at']

    def validate(self, data):
        if 'role' in data and data['role'] == ClubMember.RoleChoices.HEAD:
            if not self.context['request'].user.is_staff:
                raise serializers.ValidationError("Only admins can assign HEAD role.")

        if ClubMember.objects.filter(
                user=data['user'],
                club=data['club']
        ).exists():
            raise serializers.ValidationError("This user is already a member of this club.")

        return data


# serializers.py additions
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity', 'location_description', 'image']

class EventSerializer(serializers.ModelSerializer):
    tickets_available = serializers.IntegerField(read_only=True)
    tickets_sold = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'club', 'room', 'start_date',
                 'end_date', 'ticket_price', 'total_tickets', 'image',
                 'ticket_type', 'tickets_available', 'tickets_sold', 'created_at']
        read_only_fields = ['created_at']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'student', 'event', 'purchased_at']
        read_only_fields = ['purchased_at']

    def validate(self, data):
        if data['event'].tickets_available <= 0:
            raise serializers.ValidationError("No tickets available for this event")
        return data

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'club', 'subscribed_at']
        read_only_fields = ['subscribed_at']

class EventReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReview
        fields = ['id', 'event', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']
