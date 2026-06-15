from django.db import models
from accounts.models import Company, Candidate, EDUCATION_CHOICES

# le modele de l'offre d'emploi, de la candidature, de celle vue et de l'offre favorite

class Job(models.Model):

    class ContractType(models.TextChoices):
        CDI = "CDI",       "CDI"
        CDD = "CDD",       "CDD"
        STAGE = "STAGE",     "Stage"
        FREELANCE = "FREELANCE", "Freelance"

    class JobStatus(models.TextChoices):
        OPEN   = "open",   "Ouverte"
        CLOSED = "closed", "Fermée"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs", verbose_name="Entreprise" )
    title       = models.CharField(max_length=200, verbose_name="Intitulé du poste")
    description = models.TextField(verbose_name="Description")
    location    = models.CharField(max_length=100, verbose_name="Localisation")
    remote      = models.BooleanField(default=False, verbose_name="Télétravail possible")
    contract_type = models.CharField( max_length=20, choices=ContractType.choices, verbose_name="Type de contrat")
    status = models.CharField(max_length=10, choices=JobStatus.choices, default=JobStatus.OPEN, verbose_name="Statut")
    experience_required = models.PositiveSmallIntegerField(default=0, verbose_name="Expérience requise (années)")
    education_level_required = models.CharField(max_length=10, choices=EDUCATION_CHOICES, null=True, blank=True, verbose_name="Niveau d'études requis")
    skills_required = models.ManyToManyField("accounts.Skill", blank=True, related_name="jobs", verbose_name="Compétences requises",)
    salary_min = models.PositiveIntegerField(null=True, blank=True, verbose_name="Salaire minimum (€/an)")
    salary_max = models.PositiveIntegerField(null=True, blank=True, verbose_name="Salaire maximum (€/an)")
    deadline   = models.DateField(null=True, blank=True, verbose_name="Date limite de candidature")
    posted_at  = models.DateTimeField(auto_now_add=True, verbose_name="Publié le")
    updated_at = models.DateTimeField(auto_now=True,     verbose_name="Modifié le")

    class Meta:
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["status", "posted_at"]),   # recherche la plus fréquente
            models.Index(fields=["location"]),
            models.Index(fields=["contract_type"]),
            models.Index(fields=["remote"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.company.company_name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValidationError(
                {"salary_min": "Le salaire minimum ne peut pas dépasser le maximum."}
            )

#  Application

class Application(models.Model):

    class ApplicationStatus(models.TextChoices):
        PENDING  = "pending",  "En attente"
        ACCEPTED = "accepted", "Acceptée"
        REJECTED = "rejected", "Refusée"

    job = models.ForeignKey(Job,       on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="applications")
    cover_letter = models.TextField(null=True, blank=True, verbose_name="Lettre de motivation")
    status = models.CharField(max_length=10, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING, verbose_name="Statut")
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name="Candidaté le")
    updated_at = models.DateTimeField(auto_now=True,     verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "candidate"], name="unique_application"
            )
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["applied_at"]),
        ]

    def __str__(self):
        return f"{self.candidate.full_name} → {self.job.title}"

#  JobView  (tracking des vues)

class JobView(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="views")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="viewed_jobs")
    view_count = models.PositiveIntegerField(default=1, verbose_name="Nombre de vues")
    first_viewed_at = models.DateTimeField(auto_now_add=True, verbose_name="Premier vue le")
    last_viewed_at  = models.DateTimeField(auto_now=True, verbose_name="Dernière vue le")

    class Meta:
        verbose_name = "Vue d'offre"
        verbose_name_plural = "Vues d'offres"
        constraints = [
            models.UniqueConstraint(
                fields=["job", "candidate"], name="unique_job_view"
            )
        ]

    def __str__(self):
        return f"{self.candidate.full_name} a vu {self.job.title} ({self.view_count}x)"

#  FavoriteJob

class FavoriteJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="favorites")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="favorite_jobs")
    saved_at  = models.DateTimeField(auto_now_add=True, verbose_name="Sauvegardé le")

    class Meta:
        verbose_name = "Offre favorite"
        verbose_name_plural = "Offres favorites"
        ordering = ["-saved_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "candidate"], name="unique_favorite_job"
            )
        ]

    def __str__(self):
        return f"{self.candidate.full_name} * {self.job.title}"
