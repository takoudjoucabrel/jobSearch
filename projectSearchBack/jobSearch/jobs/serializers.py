from django.db import IntegrityError
from rest_framework import serializers

from accounts.serializers import SkillSerializer, CompanySerializer
from .models import Application, FavoriteJob, Job, JobView
from accounts.models import Skill

#  Job
class JobListSerializer(serializers.ModelSerializer):
    """Version allégée pour les listes (évite les requêtes lourdes)."""

    company_name = serializers.CharField(source="company.company_name", read_only=True)
    company_logo = serializers.ImageField(source="company.logo", read_only=True)
    skills_required = SkillSerializer(many=True, read_only=True)
    applications_count = serializers.IntegerField(read_only=True)  # annoté dans le queryset

    class Meta:
        model = Job
        fields = (
            "id", "title", "company_name", "company_logo",
            "location", "remote", "contract_type", "status",
            "experience_required", "education_level_required",
            "salary_min", "salary_max", "deadline",
            "skills_required", "applications_count", "posted_at",
        )


class JobDetailSerializer(serializers.ModelSerializer):
    """Version complète avec l'entreprise imbriquée."""

    company = CompanySerializer(read_only=True)
    skills_required = SkillSerializer(many=True, read_only=True)
    applications_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Job
        fields = (
            "id", "title", "company", "description",
            "location", "remote", "contract_type", "status",
            "experience_required", "education_level_required",
            "salary_min", "salary_max", "deadline",
            "skills_required", "applications_count", "views_count",
            "posted_at", "updated_at",
        )

class JobWriteSerializer(serializers.ModelSerializer):
    """Création / mise à jour d'une offre (réservé aux entreprises)."""

    skills_required = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        help_text="Liste de noms de compétences (créées si inexistantes).",
    )

    class Meta:
        model = Job
        exclude = ("company", "posted_at", "updated_at")

    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError(
                {"salary_min": "Le salaire minimum ne peut pas dépasser le maximum."}
            )
        return attrs

    def _handle_skills(self, instance, skills_names):
        skill_objects = [
            Skill.objects.get_or_create(name=name.strip().lower())[0]
            for name in skills_names
        ]
        instance.skills_required.set(skill_objects)

    def create(self, validated_data):
        skills_names = validated_data.pop("skills_required", [])
        # La company est injectée depuis la vue via context
        company = self.context["request"].user.company
        job = Job.objects.create(company=company, **validated_data)
        if skills_names:
            self._handle_skills(job, skills_names)
        return job

    def update(self, instance, validated_data):
        skills_names = validated_data.pop("skills_required", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if skills_names is not None:
            self._handle_skills(instance, skills_names)
        return instance

    def to_representation(self, instance):
        return JobDetailSerializer(instance, context=self.context).data
    
#  Application

class ApplicationReadSerializer(serializers.ModelSerializer):
    """Lecture d'une candidature (vue candidat ou entreprise)."""
    job_title = serializers.CharField(source="job.title", read_only=True)
    job_id = serializers.IntegerField(source="job.id", read_only=True)
    company_name = serializers.CharField(source="job.company.company_name", read_only=True)
    candidate_name = serializers.CharField(source="candidate.full_name", read_only=True)
    candidate_id = serializers.IntegerField(source="candidate.id", read_only=True)

    class Meta:
        model = Application
        fields = (
            "id", "job_id", "job_title", "company_name",
            "candidate_id", "candidate_name",
            "cover_letter", "status", "applied_at", "updated_at",
        )

class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Création d'une candidature par un candidat."""

    class Meta:
        model = Application
        fields = ("job", "cover_letter")

    def validate_job(self, job):
        if job.status != Job.JobStatus.OPEN:
            raise serializers.ValidationError("Cette offre n'est plus ouverte aux candidatures.")
        return job

    def validate(self, attrs):
        candidate = self.context["request"].user.candidate
        if Application.objects.filter(job=attrs["job"], candidate=candidate).exists():
            raise serializers.ValidationError(
                {"job": "Vous avez déjà postulé à cette offre."}
            )
        return attrs

    def create(self, validated_data):
        candidate = self.context["request"].user.candidate
        return Application.objects.create(candidate=candidate, **validated_data)

    def to_representation(self, instance):
        return ApplicationReadSerializer(instance, context=self.context).data


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Mise à jour du statut uniquement (réservé à l'entreprise)."""

    class Meta:
        model = Application
        fields = ("status",)

    def validate_status(self, value):
        allowed = (
            Application.ApplicationStatus.ACCEPTED,
            Application.ApplicationStatus.REJECTED,
        )
        if value not in allowed:
            raise serializers.ValidationError(
                "Statut invalide. Valeurs acceptées : 'accepted', 'rejected'."
            )
        return value

#  FavoriteJob

class FavoriteJobSerializer(serializers.ModelSerializer):
    """Lecture des offres favorites d'un candidat."""

    job = JobListSerializer(read_only=True)

    class Meta:
        model = FavoriteJob
        fields = ("id", "job", "saved_at")

#  JobView  (interne — pas exposé directement)

class JobViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobView
        fields = ("id", "job", "view_count", "first_viewed_at", "last_viewed_at")
        read_only_fields = fields


