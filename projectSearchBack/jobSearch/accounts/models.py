from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


# ─────────────────────────────────────────────
#  User
# ─────────────────────────────────────────────

class User(AbstractUser):
    username = None

    USER_TYPE_CHOICES = [
        ("candidate", "Candidat"),
        ("company", "Entreprise"),
    ]

    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        verbose_name="Type d'utilisateur",
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="E-mail vérifié",
        help_text="Activé après confirmation de l'adresse e-mail.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        # Empêche un user "candidate" d'avoir un profil Company et vice-versa
        if self.user_type == "candidate" and hasattr(self, "company"):
            raise ValidationError("Un candidat ne peut pas avoir un profil entreprise.")
        if self.user_type == "company" and hasattr(self, "candidate"):
            raise ValidationError("Une entreprise ne peut pas avoir un profil candidat.")

    @property
    def profile(self):
        """Retourne le profil associé (Candidate ou Company) ou None."""
        if self.user_type == "candidate":
            return getattr(self, "candidate", None)
        if self.user_type == "company":
            return getattr(self, "company", None)
        return None


# ─────────────────────────────────────────────
#  Skill  (table dédiée pour filtrage efficace)
# ─────────────────────────────────────────────

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Compétence")

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
#  Candidate
# ─────────────────────────────────────────────

EDUCATION_CHOICES = [
    ("bac", "Baccalauréat"),
    ("bac+2", "Bac+2 (BTS / DUT)"),
    ("bac+3", "Bac+3 (Licence)"),
    ("bac+5", "Bac+5 (Master / Ingénieur)"),
    ("bac+8", "Bac+8 (Doctorat)"),
    ("other", "Autre"),
]


class Candidate(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="candidate",
        verbose_name="Utilisateur",
    )
    full_name = models.CharField(max_length=250, verbose_name="Nom complet")
    city = models.CharField(max_length=200, verbose_name="Ville")
    phone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Téléphone"
    )
    bio = models.TextField(
        null=True, blank=True, verbose_name="Présentation",
        help_text="Résumé du profil affiché aux recruteurs."
    )
    experience_years = models.PositiveSmallIntegerField(
        verbose_name="Années d'expérience"
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="candidates",
        verbose_name="Compétences",
    )
    education_level = models.CharField(
        max_length=10,
        choices=EDUCATION_CHOICES,
        verbose_name="Niveau d'études",
    )
    linkedin = models.URLField(
        null=True, blank=True, verbose_name="Profil LinkedIn"
    )
    cv = models.FileField(
        upload_to="cvs/",
        null=True,
        blank=True,
        verbose_name="CV (fichier)",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="En recherche d'emploi",
        help_text="Indique si le candidat est actuellement disponible.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Candidat"
        verbose_name_plural = "Candidats"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.user.email})"


# ─────────────────────────────────────────────
#  Company
# ─────────────────────────────────────────────

class Company(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="company",
        verbose_name="Utilisateur",
    )
    company_name = models.CharField(max_length=250, verbose_name="Nom de l'entreprise")
    logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True,
        verbose_name="Logo",
    )
    description = models.TextField(verbose_name="Description")
    location = models.CharField(max_length=200, verbose_name="Localisation")
    phone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Téléphone"
    )
    website = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="Site web"
    )
    sector = models.CharField(max_length=100, verbose_name="Secteur d'activité")
    employee_count = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Nombre d'employés"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Entreprise vérifiée",
        help_text="Activé manuellement par un administrateur.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
        ordering = ["-created_at"]

    def __str__(self):
        return self.company_name
