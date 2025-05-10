from rest_framework import generics, permissions, views
from rest_framework.response import Response
from .serializers import *
from rest_framework.exceptions import PermissionDenied
from .permissions import *
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from django.utils import timezone

class CurrentStudentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = StudentSerializer(request.user)
        return Response(serializer.data)


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminOrHeadOfThisClub()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save()


class StudentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_update(self, serializer):
        serializer.save()


class ClubListCreateView(generics.ListCreateAPIView):
    queryset = Club.objects.all().prefetch_related('members', 'events')
    serializer_class = ClubSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can create clubs.")
        serializer.save()


class ClubDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Club.objects.all().prefetch_related('members', 'events')
    serializer_class = ClubSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can update clubs.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can delete clubs.")
        instance.delete()


class ClubMemberListCreateView(generics.ListCreateAPIView):
    serializer_class = ClubMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        club_pk = self.kwargs.get('club_pk')
        if club_pk:
            return ClubMember.objects.filter(club_id=club_pk).select_related('user', 'club')
        return ClubMember.objects.all().select_related('user', 'club')

    def perform_create(self, serializer):
        club_pk = self.kwargs.get('club_pk')
        if club_pk:
           club = Club.objects.get(pk=club_pk)
           serializer.save(club=club)
        else:
            serializer.save()


class ClubMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClubMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHeadOfThisClub]
    queryset = ClubMember.objects.all()

    def perform_update(self, serializer):
        instance = self.get_object()
        new_role = serializer.validated_data.get('role')
        if new_role == ClubMember.RoleChoices.HEAD and not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can assign the HEAD role.")
        serializer.save()

class UserClubMembershipsView(generics.ListAPIView):
    serializer_class = ClubMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')

        if int(user_pk) == self.request.user.id:
            return ClubMember.objects.filter(user_id=user_pk).select_related('user', 'club')

        if self.request.user.is_staff:
            return ClubMember.objects.filter(user_id=user_pk).select_related('user', 'club')

        # Cache this query result to avoid multiple DB hits
        head_clubs = list(ClubMember.objects.filter(
            user=self.request.user,
            role=ClubMember.RoleChoices.HEAD
        ).values_list('club_id', flat=True))

        return ClubMember.objects.filter(
            user_id=user_pk,
            club_id__in=head_clubs
        ).select_related('user', 'club')


class ClubHeadAssignView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, club_pk, user_pk):
        try:
            club = Club.objects.get(pk=club_pk)
            user = Student.objects.get(pk=user_pk)

            membership, created = ClubMember.objects.get_or_create(
                user=user,
                club=club,
                defaults={'role': ClubMember.RoleChoices.HEAD}
            )

            if not created:
                membership.role = ClubMember.RoleChoices.HEAD
                membership.save()
                return Response(
                    {"message": f"User {user.username} updated to head of {club.name}"},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"message": f"User {user.username} assigned as head of {club.name}"},
                status=status.HTTP_201_CREATED
            )

        except Club.DoesNotExist:
            return Response(
                {"error": "Club not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Student.DoesNotExist:
            return Response(
                {"error": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can create rooms.")
        serializer.save()


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can update rooms.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can delete rooms.")
        instance.delete()


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all().select_related('club', 'room')

        club_pk = self.kwargs.get('club_pk')
        if club_pk:
            queryset = queryset.filter(club_id=club_pk)

        upcoming = self.request.query_params.get('upcoming')
        if upcoming == 'true':
            queryset = queryset.filter(start_date__gte=timezone.now())

        return queryset


    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser(), IsAdminOrHeadOfThisClub()]


    def perform_create(self, serializer):
        club_pk = self.kwargs.get('club_pk')
        if club_pk:
            club = Club.objects.get(pk=club_pk)

            if not self.request.user.is_staff and not ClubMember.objects.filter(
                    user=self.request.user,
                    club=club,
                    role=ClubMember.RoleChoices.HEAD
            ).exists():
                raise PermissionDenied("Only admin users or club heads can create events.")

            serializer.save(club=club)
        else:
            club = serializer.validated_data.get('club')
            if not self.request.user.is_staff and not ClubMember.objects.filter(
                    user=self.request.user,
                    club=club,
                    role=ClubMember.RoleChoices.HEAD
            ).exists():
                raise PermissionDenied("Only admin users or club heads can create events.")

            serializer.save()


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all().select_related('club', 'room')
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser(), IsAdminOrHeadOfThisClub()]

    def perform_update(self, serializer):
        instance = self.get_object()
        if not self.request.user.is_staff and not ClubMember.objects.filter(
                user=self.request.user,
                club=instance.club,
                role=ClubMember.RoleChoices.HEAD
        ).exists():
            raise PermissionDenied("Only admin users or club heads can update events.")

        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and not ClubMember.objects.filter(
                user=self.request.user,
                club=instance.club,
                role=ClubMember.RoleChoices.HEAD
        ).exists():
            raise PermissionDenied("Only admin users or club heads can delete events.")

        instance.delete()


class TicketListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer

    def get_queryset(self):
        event_pk = self.kwargs.get('event_pk')
        if event_pk:
            return Ticket.objects.filter(event_id=event_pk).select_related('event', 'student', 'event__club')

        if self.request.user.is_staff:
            return Ticket.objects.all().select_related('event', 'student', 'event__club')

        # Cache head_clubs to avoid multiple DB hits
        head_clubs = list(ClubMember.objects.filter(
            user=self.request.user,
            role=ClubMember.RoleChoices.HEAD
        ).values_list('club_id', flat=True))

        # Cache club_events to avoid multiple DB hits
        club_events = list(Event.objects.filter(club_id__in=head_clubs).values_list('id', flat=True))

        return Ticket.objects.filter(
            Q(student=self.request.user) | Q(event_id__in=club_events)
        ).select_related('event', 'student', 'event__club')

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    from django.db import transaction
    @transaction.atomic
    def perform_create(self, serializer):
        event = serializer.validated_data.get('event')
        student = serializer.validated_data.get('student', self.request.user)

        if student.id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied("You can only purchase tickets for yourself.")

        if event.tickets_available <= 0:
            raise serializers.ValidationError({"event": "No tickets available for this event."})

        if event.ticket_type == Event.TicketTypeChoices.PAID:
            if student.wallet_balance < event.ticket_price:
                raise serializers.ValidationError({"wallet": "Insufficient wallet balance."})

            student.wallet_balance -= event.ticket_price
            student.save()

        serializer.save(student=student)


class TicketDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = TicketSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Ticket.objects.all().select_related('event', 'student', 'event__club')

        # Cache head_clubs to avoid multiple DB hits
        head_clubs = list(ClubMember.objects.filter(
            user=self.request.user,
            role=ClubMember.RoleChoices.HEAD
        ).values_list('club_id', flat=True))

        # Cache club_events to avoid multiple DB hits
        club_events = list(Event.objects.filter(club_id__in=head_clubs).values_list('id', flat=True))

        return Ticket.objects.filter(
            Q(student=self.request.user) | Q(event_id__in=club_events)
        ).select_related('event', 'student', 'event__club')


    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        if instance.student != self.request.user and not self.request.user.is_staff:
            is_club_head = ClubMember.objects.filter(
                user=self.request.user,
                club=instance.event.club,
                role=ClubMember.RoleChoices.HEAD
            ).exists()

            if not is_club_head:
                raise PermissionDenied("You can only cancel your own tickets.")

        if instance.event.ticket_type == Event.TicketTypeChoices.PAID:
            student = instance.student
            student.wallet_balance += instance.event.ticket_price
            student.save()

        instance.delete()


class StudentTicketsView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student_pk = self.kwargs.get('student_pk', self.request.user.id)

        if student_pk != self.request.user.id and not self.request.user.is_staff:
            # Cache head_clubs to avoid multiple DB hits
            head_clubs = list(ClubMember.objects.filter(
                user=self.request.user,
                role=ClubMember.RoleChoices.HEAD
            ).values_list('club_id', flat=True))

            if not head_clubs:
                raise PermissionDenied("You can only view your own tickets.")

            student_clubs = ClubMember.objects.filter(
                user_id=student_pk,
                club_id__in=head_clubs
            )

            if not student_clubs:
                raise PermissionDenied("You can only view tickets for members of clubs you head.")

        return Ticket.objects.filter(student_id=student_pk).select_related('event', 'student', 'event__club')






class SubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        club_pk = self.kwargs.get('club_pk')
        if club_pk:
            return Subscription.objects.filter(club_id=club_pk).select_related('user', 'club')

        user_pk = self.kwargs.get('user_pk')
        if user_pk:
            return Subscription.objects.filter(user_id=user_pk).select_related('user', 'club')

        return Subscription.objects.filter(user=self.request.user).select_related('user', 'club')


    def perform_create(self, serializer):
        user = serializer.validated_data.get('user', self.request.user)

        if user.id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied("You can only subscribe yourself.")

        club_pk = self.kwargs.get('club_pk')
        if club_pk:
            club = Club.objects.get(pk=club_pk)
            serializer.save(user=user, club=club)
        else:
            serializer.save(user=user)


class SubscriptionDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Subscription.objects.all().select_related('user', 'club')
        return Subscription.objects.filter(user=self.request.user).select_related('user', 'club')

    def perform_destroy(self, instance):
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You can only unsubscribe yourself.")
        instance.delete()


class EventReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = EventReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        event_pk = self.kwargs.get('event_pk')
        if event_pk:
            return EventReview.objects.filter(event_id=event_pk).select_related('user', 'event', 'event__club')

        if self.request.user.is_staff:
            return EventReview.objects.all().select_related('user', 'event', 'event__club')

        # Optimize the complex query with select_related
        return EventReview.objects.filter(
            Q(user=self.request.user) | Q(event__club__members__user=self.request.user,
                                          event__club__members__role=ClubMember.RoleChoices.HEAD)
        ).select_related('user', 'event', 'event__club').distinct()

    def perform_create(self, serializer):
        user =  self.request.user
        print(user.username)

        if user.id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied("You can only create reviews for yourself.")

        event_pk = self.kwargs.get('event_pk')
        if event_pk:
            event = Event.objects.get(pk=event_pk)

            if not Ticket.objects.filter(event=event, student=user).exists():
                raise serializers.ValidationError(
                    {"event": "You can only review events you have tickets for."}
                )

            serializer.save(user=user, event=event)
        else:
            serializer.save(user=user)


class EventReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return EventReview.objects.all().select_related('user', 'event', 'event__club')

        # Optimize the complex query with select_related
        return EventReview.objects.filter(
            Q(user=self.request.user) | Q(event__club__members__user=self.request.user,
                                          event__club__members__role=ClubMember.RoleChoices.HEAD)
        ).select_related('user', 'event', 'event__club').distinct()

    def perform_update(self, serializer):
        instance = self.get_object()

        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You can only update your own reviews.")

        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user and not self.request.user.is_staff:
            is_club_head = ClubMember.objects.filter(
                user=self.request.user,
                club=instance.event.club,
                role=ClubMember.RoleChoices.HEAD
            ).exists()

            if not is_club_head:
                raise PermissionDenied("You cannot delete this review.")

        instance.delete()