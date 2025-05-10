from rest_framework import permissions

from core.models import ClubMember


class IsAdminOrHeadOfThisClub(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

        club_pk = view.kwargs.get('club_pk')
        if club_pk:
            return ClubMember.objects.filter(
                user=request.user,
                club_id=club_pk,
                role=ClubMember.RoleChoices.HEAD
            ).exists()

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if isinstance(obj, ClubMember):
            return ClubMember.objects.filter(
                user=request.user,
                club=obj.club,
                role=ClubMember.RoleChoices.HEAD
            ).exists()

        return False