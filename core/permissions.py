from rest_framework import permissions

from core.models import ClubMember


class IsAdminOrClubHead(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_staff or
                ClubMember.objects.filter
                (user=request.user, role=ClubMember.RoleChoices.HEAD).exists())


class IsAdminOrHeadOfThisClub(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return ClubMember.objects.filter(
            user=request.user,
            club=obj.club,
            role=ClubMember.RoleChoices.HEAD
        ).exists()