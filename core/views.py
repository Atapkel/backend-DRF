from rest_framework import generics, permissions, views
from rest_framework.response import Response
from .serializers import *
from rest_framework.exceptions import PermissionDenied
from .permissions import IsAdminOrClubHead, IsAdminOrHeadOfThisClub


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
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can create clubs.")
        serializer.save()


class ClubDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
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
    queryset = ClubMember.objects.all()
    serializer_class = ClubMemberSerializer
    permission_classes = [IsAdminOrClubHead]

    def get_queryset(self):
        club_id = self.kwargs['clubId']
        return ClubMember.objects.filter(club_id=club_id)

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            club = serializer.validated_data['club']
            if not ClubMember.objects.filter(
                user=self.request.user,
                club=club,
                role=ClubMember.RoleChoices.HEAD
            ).exists():
                raise PermissionDenied("You cann't add members to this club.")

        serializer.save()

class ClubMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClubMember.objects.all()
    serializer_class = ClubMemberSerializer
    permission_classes = [IsAdminOrHeadOfThisClub]



    def perform_update(self, serializer):
        if 'role' in serializer.validated_data and not self.request.user.is_staff:
            raise PermissionDenied("Only admins can change roles.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            if not ClubMember.objects.filter(
                    user=self.request.user,
                    club=instance.club,
                    role=ClubMember.RoleChoices.HEAD
            ).exists():
                raise PermissionDenied("You can't remove members from this club.")
        instance.delete()


# views.py additions
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrClubHead]

    def perform_create(self, serializer):
        club = serializer.validated_data['club']
        if not self.request.user.is_staff:
            if not ClubMember.objects.filter(
                user=self.request.user,
                club=club,
                role=ClubMember.RoleChoices.HEAD
            ).exists():
                raise PermissionDenied("Only club heads can create events")
        serializer.save()

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrClubHead]

class TicketListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class SubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SubscriptionDetailView(generics.DestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

class EventReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = EventReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventReview.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EventReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventReview.objects.all()
    serializer_class = EventReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventReview.objects.filter(user=self.request.user)