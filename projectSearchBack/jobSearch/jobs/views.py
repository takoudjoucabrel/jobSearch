from django.db import IntegrityError
from django.db.models import Count, Q
from rest_framework import filters, generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Application, FavoriteJob, Job, JobView
from rest_framework.exceptions import NotFound

from .serializers import (
    ApplicationCreateSerializer,
    ApplicationReadSerializer,
    ApplicationStatusSerializer,
    FavoriteJobSerializer,
    JobDetailSerializer,
    JobListSerializer,
    JobWriteSerializer,
)
from accounts.permissions import (
    IsApplicationOwner,
    IsCandidateUser,
    IsCompanyUser,
    IsJobOwnerCompany,
)

#  Offres d'emploi

class JobListView(generics.ListAPIView):
    serializer_class = JobListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("title", "description", "skills_required__name", "company__company_name")
    ordering_fields = ("posted_at", "salary_min", "experience_required")
    ordering = ("-posted_at",)

    def get_queryset(self):
        qs = (
            Job.objects
            .select_related("company")
            .prefetch_related("skills_required")
            .annotate(
                applications_count=Count("applications", distinct=True),
                views_count=Count("views", distinct=True),
            )
        )

        params = self.request.query_params

        location      = params.get("location")
        contract_type = params.get("contract_type")
        remote        = params.get("remote")
        min_salary    = params.get("min_salary")
        skills_param  = params.get("skills")
        job_status    = params.get("status", Job.JobStatus.OPEN)

        if location:
            qs = qs.filter(location__icontains=location)
        if contract_type:
            qs = qs.filter(contract_type=contract_type)
        if remote is not None:
            qs = qs.filter(remote=remote.lower() == "true")
        if min_salary:
            qs = qs.filter(
                Q(salary_max__gte=min_salary) | Q(salary_max__isnull=True)
            )
        if skills_param:
            for skill in skills_param.split(","):
                qs = qs.filter(skills_required__name__icontains=skill.strip())
        if job_status:
            qs = qs.filter(status=job_status)

        return qs.distinct()


class JobDetailView(generics.RetrieveAPIView):
    """
    GET /jobs/<id>/
    Retourne le détail complet d'une offre.
    Enregistre automatiquement une vue si l'utilisateur est un candidat.
    """
    serializer_class = JobDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            Job.objects
            .select_related("company")
            .prefetch_related("skills_required")
            .annotate(
                applications_count=Count("applications", distinct=True),
                views_count=Count("views", distinct=True),
            )
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Enregistrement de la vue si candidat
        if request.user.user_type == "candidate":
            candidate = getattr(request.user, "candidate", None)
            if candidate:
                job_view, created = JobView.objects.get_or_create(
                    job=instance, candidate=candidate
                )
                if not created:
                    JobView.objects.filter(pk=job_view.pk).update(
                        view_count=job_view.view_count + 1
                    )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class JobCreateView(generics.CreateAPIView):
    """
    POST /jobs/
    Crée une offre d'emploi (entreprise uniquement).
    """
    serializer_class = JobWriteSerializer
    permission_classes = (permissions.IsAuthenticated, IsCompanyUser)


class JobUpdateView(generics.UpdateAPIView):
    """
    PUT  /jobs/<id>/edit/
    PATCH /jobs/<id>/edit/
    Modifie une offre (propriétaire uniquement).
    """
    serializer_class = JobWriteSerializer
    permission_classes = (permissions.IsAuthenticated, IsJobOwnerCompany)
    queryset = Job.objects.all()


class JobDeleteView(generics.DestroyAPIView):
    """
    DELETE /jobs/<id>/delete/
    Supprime une offre (propriétaire uniquement).
    """
    permission_classes = (permissions.IsAuthenticated, IsJobOwnerCompany)
    queryset = Job.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "Offre supprimée avec succès."},
            status=status.HTTP_204_NO_CONTENT,
        )


class CompanyJobListView(generics.ListAPIView):
    """
    GET /jobs/company/me/
    Liste des offres de l'entreprise connectée.
    """
    serializer_class = JobListSerializer
    permission_classes = (permissions.IsAuthenticated, IsCompanyUser)

    def get_queryset(self):
        return (
            Job.objects
            .filter(company__user=self.request.user)
            .annotate(
                applications_count=Count("applications", distinct=True),
                views_count=Count("views", distinct=True),
            )
            .prefetch_related("skills_required")
        )

#  Candidatures

class ApplicationCreateView(generics.CreateAPIView):
    """
    POST /jobs/<job_id>/apply/
    Le candidat postule à une offre.
    """
    serializer_class = ApplicationCreateSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidateUser)

    def perform_create(self, serializer):
        serializer.save()

class ApplicationListView(generics.ListAPIView):
    """
    GET /applications/
    - Candidat  → ses propres candidatures
    - Entreprise → candidatures reçues sur ses offres
    """
    serializer_class = ApplicationReadSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ("applied_at", "status")
    ordering = ("-applied_at",)

    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.select_related(
            "job", "job__company", "candidate"
        )
        if user.user_type == "candidate":
            return qs.filter(candidate__user=user)
        if user.user_type == "company":
            status_filter = self.request.query_params.get("status")
            qs = qs.filter(job__company__user=user)
            if status_filter:
                qs = qs.filter(status=status_filter)
            return qs
        return qs.none()

class ApplicationDetailView(generics.RetrieveAPIView):
    """
    GET /applications/<id>/
    Lecture d'une candidature (candidat concerné ou entreprise concernée).
    """
    serializer_class = ApplicationReadSerializer
    permission_classes = (permissions.IsAuthenticated, IsApplicationOwner)
    queryset = Application.objects.select_related("job", "job__company", "candidate")

class ApplicationStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /applications/<id>/status/
    L'entreprise accepte ou refuse une candidature.
    """
    serializer_class = ApplicationStatusSerializer
    permission_classes = (permissions.IsAuthenticated, IsCompanyUser)
    queryset = Application.objects.select_related("job__company")
    http_method_names = ("patch",)

    def get_object(self):
        obj = super().get_object()
        if obj.job.company.user != self.request.user:
            raise PermissionDenied("Vous n'êtes pas propriétaire de cette offre.")
        return obj

class ApplicationWithdrawView(APIView):
    """
    DELETE /applications/<id>/withdraw/
    Le candidat retire sa candidature (seulement si PENDING).
    """
    permission_classes = (permissions.IsAuthenticated, IsCandidateUser)

    def delete(self, request, pk):
        try:
            application = Application.objects.get(pk=pk, candidate__user=request.user)
        except Application.DoesNotExist:
            return Response(
                {"detail": "Candidature introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if application.status != Application.ApplicationStatus.PENDING:
            return Response(
                {"detail": "Impossible de retirer une candidature déjà traitée."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application.delete()
        return Response(
            {"detail": "Candidature retirée avec succès."},
            status=status.HTTP_204_NO_CONTENT,
        )

#  Favoris

class FavoriteJobListView(generics.ListAPIView):
    """
    GET /favorites/
    Liste des offres favorites du candidat connecté.
    """
    serializer_class = FavoriteJobSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidateUser)

    def get_queryset(self):
        return FavoriteJob.objects.filter(
            candidate__user=self.request.user
        ).select_related("job", "job__company").prefetch_related("job__skills_required")


class FavoriteJobToggleView(APIView):
    """
    POST   /jobs/<job_id>/favorite/  → ajoute aux favoris
    DELETE /jobs/<job_id>/favorite/  → retire des favoris
    """
    permission_classes = (permissions.IsAuthenticated, IsCandidateUser)

    def _get_job(self, job_id):
        try:
            return Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            raise NotFound("Offre introuvable.")

    def post(self, request, job_id):
        job = self._get_job(job_id)
        candidate = request.user.candidate
        try:
            FavoriteJob.objects.create(job=job, candidate=candidate)
        except IntegrityError:
            return Response(
                {"detail": "Cette offre est déjà dans vos favoris."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Offre ajoutée aux favoris."},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, job_id):
        job = self._get_job(job_id)
        deleted, _ = FavoriteJob.objects.filter(
            job=job, candidate__user=request.user
        ).delete()
        if not deleted:
            return Response(
                {"detail": "Cette offre n'est pas dans vos favoris."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"detail": "Offre retirée des favoris."},
            status=status.HTTP_204_NO_CONTENT,
        )
