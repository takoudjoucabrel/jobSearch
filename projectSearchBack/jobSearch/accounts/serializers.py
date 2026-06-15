from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Candidate, Company, User, Skill

#  Helpers

class UserMinimalSerializer(serializers.ModelSerializer):
    """Représentation légère de l'utilisateur (utilisée dans les réponses auth)."""
    class Meta:
        model = User
        fields = ("id", "email", "user_type")
        read_only_fields = fields

#  Profils

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        exclude = ("user",)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ("user",)

#  Inscription

class RegisterSerializer(serializers.ModelSerializer):
    """
    Crée un User + son profil (Candidate ou Company) en une seule requête.

    Payload attendu
    ---------------
    Champs communs :
        email, password, confirm_password, user_type

    Si user_type == "candidate" :
        full_name, city, experience_years, skills, education_level, cv (optionnel)

    Si user_type == "company" :
        company_name, description, location, sector, website (optionnel), logo (optionnel)
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    # Champs Candidate (optionnels au niveau sérialiseur, validés selon user_type)
    full_name = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    experience_years = serializers.IntegerField(required=False, min_value=0)
    skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    education_level = serializers.CharField(required=False)
    cv = serializers.FileField(required=False, allow_null=True)

    # Champs Company (optionnels au niveau sérialiseur, validés selon user_type)
    company_name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    sector = serializers.CharField(required=False)
    website = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "confirm_password",
            "user_type",
            # candidate
            "full_name",
            "city",
            "experience_years",
            "skills",
            "education_level",
            "cv",
            # company
            "company_name",
            "description",
            "location",
            "sector",
            "website",
            "logo",
        )

    # ── Validation globale ────────────────────

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})

        user_type = attrs.get("user_type")
        if user_type not in ("candidate", "company"):
            raise serializers.ValidationError({"user_type": "Valeur invalide. Choisissez 'candidate' ou 'company'."})

        if user_type == "candidate":
            required = ("full_name", "city", "experience_years", "education_level")
            missing = [f for f in required if not attrs.get(f) and attrs.get(f) != 0]
            if missing:
                raise serializers.ValidationError({f: "Ce champ est requis pour un candidat." for f in missing})

        if user_type == "company":
            required = ("company_name", "description", "location", "sector")
            missing = [f for f in required if not attrs.get(f)]
            if missing:
                raise serializers.ValidationError({f: "Ce champ est requis pour une entreprise." for f in missing})
        return attrs

    # Création

    def create(self, validated_data):
        user_type = validated_data["user_type"]

        # Séparer les champs profil des champs User
        candidate_fields = ("full_name", "city", "experience_years", "skills", "education_level", "cv")
        company_fields = ("company_name", "description", "location", "sector", "website", "logo")

        profile_data = {}
        for field in candidate_fields + company_fields:
            value = validated_data.pop(field, None)
            if value is not None:
                profile_data[field] = value

        # Extraire skills à part (ManyToMany)
        skills_data = profile_data.pop("skills", None)

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            user_type=user_type,
        )

        if user_type == "candidate":
            candidate = Candidate.objects.create(user=user, **profile_data)
            if skills_data:
                candidate.skills.set(skills_data)
        else:
            Company.objects.create(user=user, **profile_data)

        return user
    def to_representation(self, instance):
        """Retourne le token JWT + les infos utilisateur après inscription."""
        refresh = RefreshToken.for_user(instance)
        return {
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "user": UserMinimalSerializer(instance).data,
        }

#  Connexion

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email", "").lower().strip()
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), username=email, password=password)
        if not user:
            raise serializers.ValidationError({"non_field_errors": "Email ou mot de passe incorrect."})
        if not user.is_active:
            raise serializers.ValidationError({"non_field_errors": "Ce compte est désactivé."})
        attrs["user"] = user
        return attrs

    def to_representation(self, instance):
        user = instance["user"]
        refresh = RefreshToken.for_user(user)
        return {
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "user": UserMinimalSerializer(user).data,
        }

#  Réinitialisation du mot de passe — étape 1
#  (demande d'envoi d'e-mail)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # On ne révèle PAS si l'adresse existe (protection contre l'énumération)
        return value.lower().strip()

#  Réinitialisation du mot de passe — étape 2
#  (confirmation avec le token reçu par e-mail)

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Les mots de passe ne correspondent pas."}
            )

        # Décoder l'UID
        try:
            uid = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError({"uid": "Lien invalide ou expiré."})

        # Vérifier le token
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "Lien invalide ou expiré."})

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user

#  Changement de mot de passe (utilisateur connecté)

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
    
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("name",)    


