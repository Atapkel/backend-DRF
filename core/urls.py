from django.urls import path
from .views import *


urlpatterns = [
    path('students/', StudentListCreateView.as_view(), name='student-list'),
    path('students/<int:pk>/', StudentDetailAPIView.as_view(), name='student-detail'),
    path('students/current/', CurrentStudentView.as_view(), name='current-student'),

    path('clubs/', ClubListCreateView.as_view(), name='club-list'),
    path('clubs/<int:pk>/', ClubDetailAPIView.as_view(), name='club-detail'),
    path('clubs/<int:clubId>/members/', ClubMemberListCreateView.as_view(), name='club-members-list'),
    path('clubs/<int:clubId>/members/<int:pk>/', ClubMemberDetailView.as_view(), name='club-members-detail'),
    path('events/'    , EventListCreateView.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('rooms/', RoomListCreateView.as_view(), name='room-list'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    #
    path('tickets/', TicketListCreateView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscription-list'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('event-reviews/', EventReviewListCreateView.as_view(), name='eventreview-list'),
    path('event-reviews/<int:pk>/', EventReviewDetailView.as_view(), name='eventreview-detail'),
]
