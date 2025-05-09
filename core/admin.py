from django.contrib import admin
from .models import Student, Club, ClubMember, Event, Room, Ticket, EventReview, Subscription


admin.site.register(Student)
admin.site.register(Club)
admin.site.register(ClubMember)
admin.site.register(Event)
admin.site.register(Room)
admin.site.register(Ticket)
admin.site.register(EventReview)
admin.site.register(Subscription)

