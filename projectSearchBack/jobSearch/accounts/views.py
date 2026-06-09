from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
)
from .tasks import send_password_reset_email  # Celery task 


class RegisterView(generics.CreateAPIView):
    """
    POST /auth/register/
    Crée un compte (candidat ou entreprise) et retourne les tokens JWT.
    """

    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            serializer.to_representation({"user": user}),
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /auth/login/
    Retourne les tokens JWT si les identifiants sont valides.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.to_representation(serializer.validated_data))


class LogoutView(APIView):
    """
    POST /auth/logout/
    Invalide le refresh token (blacklist).
    Body : { "refresh": "<token>" }
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Le champ 'refresh' est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Token invalide ou déjà révoqué."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    POST /auth/password-reset/
    Envoie un e-mail de réinitialisation si l'adresse existe.
    Body : { "email": "..." }
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            token_generator = PasswordResetTokenGenerator()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            # Envoi asynchrone via Celery (remplacer par send_mail() si pas de Celery)
            send_password_reset_email.delay(
                user_email=user.email,
                uid=uid,
                token=token,
            )
        except User.DoesNotExist:
            pass  # On répond toujours 200 pour ne pas révéler les e-mails enregistrés

        return Response(
            {
                "detail": (
                    "Si cette adresse est associée à un compte, "
                    "un e-mail de réinitialisation a été envoyé."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    POST /auth/password-reset/confirm/
    Valide le token et applique le nouveau mot de passe.
    Body : { "uid": "...", "token": "...", "new_password": "...", "confirm_password": "..." }
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Mot de passe réinitialisé avec succès."},
            status=status.HTTP_200_OK,
        )


class PasswordChangeView(APIView):
    """
    POST /auth/password-change/
    Change le mot de passe de l'utilisateur connecté.
    Body : { "old_password": "...", "new_password": "...", "confirm_password": "..." }
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Mot de passe modifié avec succès."},
            status=status.HTTP_200_OK,
        )
