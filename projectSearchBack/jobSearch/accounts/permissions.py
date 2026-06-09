from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCompanyUser(BasePermission):
    """Réservé aux utilisateurs de type 'company'."""
    message = "Seules les entreprises peuvent effectuer cette action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_type == "company"
        )


class IsJobOwnerCompany(BasePermission):
    """L'entreprise ne peut modifier/supprimer que SES propres offres."""
    message = "Vous n'êtes pas propriétaire de cette offre."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_type == "company"
        )

    def has_object_permission(self, request, view, obj):
        return obj.company.user == request.user


class IsCandidateUser(BasePermission):
    """Réservé aux utilisateurs de type 'candidate'."""
    message = "Seuls les candidats peuvent effectuer cette action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_type == "candidate"
        )


class IsApplicationOwner(BasePermission):
    """
    Lecture : candidat propriétaire OU entreprise concernée.
    Modification du statut : entreprise concernée uniquement.
    """
    message = "Vous n'avez pas accès à cette candidature."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.user_type == "candidate":
            return obj.candidate.user == user
        if user.user_type == "company":
            return obj.job.company.user == user
        return False
