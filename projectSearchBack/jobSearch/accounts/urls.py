from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
)

urlpatterns = [
    # Inscription / Connexion / Déconnexion
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),

    # Rafraîchissement du token JWT
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Réinitialisation du mot de passe (flux en 2 étapes)
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),

    # Changement de mot de passe (utilisateur connecté)
    path("password-change/", PasswordChangeView.as_view(), name="password-change"),
]
