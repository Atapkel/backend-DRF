from django.urls import path
from . import views

urlpatterns = [

    path('students/', views.StudentListCreateView.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetailAPIView.as_view(), name='student-detail'),
    path('students/current/', views.CurrentStudentView.as_view(), name='current-student'),
    path('students/<int:student_pk>/tickets/', views.StudentTicketsView.as_view(), name='student-tickets'),
    path('students/<int:user_pk>/clubs/', views.UserClubMembershipsView.as_view(), name='user-clubs'),
    path('students/<int:user_pk>/subscriptions/', views.SubscriptionListCreateView.as_view(),
         name='user-subscriptions'),


    path('clubs/', views.ClubListCreateView.as_view(), name='club-list'),
    path('clubs/<int:pk>/', views.ClubDetailAPIView.as_view(), name='club-detail'),
    path('clubs/<int:club_pk>/members/', views.ClubMemberListCreateView.as_view(), name='club-members'),
    path('clubs/<int:club_pk>/events/', views.EventListCreateView.as_view(), name='club-events'),
    path('clubs/<int:club_pk>/subscriptions/', views.SubscriptionListCreateView.as_view(), name='club-subscriptions'),
    path('clubs/<int:club_pk>/head/<int:user_pk>/', views.ClubHeadAssignView.as_view(), name='club-head-assign'),


    path('memberships/<int:pk>/', views.ClubMemberDetailView.as_view(), name='membership-detail'),


    path('rooms/', views.RoomListCreateView.as_view(), name='room-list'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room-detail'),


    path('events/', views.EventListCreateView.as_view(), name='event-list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/<int:event_pk>/tickets/', views.TicketListCreateView.as_view(), name='event-tickets'),
    path('events/<int:event_pk>/reviews/', views.EventReviewListCreateView.as_view(), name='event-reviews'),


    path('tickets/', views.TicketListCreateView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket-detail'),


    path('subscriptions/', views.SubscriptionListCreateView.as_view(), name='subscription-list'),
    path('subscriptions/<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription-detail'),


    path('reviews/', views.EventReviewListCreateView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.EventReviewDetailView.as_view(), name='review-detail')
]