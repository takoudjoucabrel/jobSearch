from django.urls import path

from .views import (
    # Offres
    JobListView,
    JobDetailView,
    JobCreateView,
    JobUpdateView,
    JobDeleteView,
    CompanyJobListView,
    # Candidatures
    ApplicationCreateView,
    ApplicationListView,
    ApplicationDetailView,
    ApplicationStatusUpdateView,
    ApplicationWithdrawView,
    # Favoris
    FavoriteJobListView,
    FavoriteJobToggleView,
)

urlpatterns = [

    # ── Offres d'emploi ───────────────────────────────────────────────────
    # Ordre important : les routes statiques (/me/, /create/) avant les dynamiques (<id>/)
    path("jobs/",                       JobListView.as_view(),          name="job-list"),
    path("jobs/create/",                JobCreateView.as_view(),        name="job-create"),
    path("jobs/company/me/",            CompanyJobListView.as_view(),   name="job-company-mine"),
    path("jobs/<int:pk>/",              JobDetailView.as_view(),        name="job-detail"),
    path("jobs/<int:pk>/edit/",         JobUpdateView.as_view(),        name="job-edit"),
    path("jobs/<int:pk>/delete/",       JobDeleteView.as_view(),        name="job-delete"),

    # ── Candidatures ──────────────────────────────────────────────────────
    path("jobs/<int:job_id>/apply/",            ApplicationCreateView.as_view(),        name="application-create"),
    path("applications/",                       ApplicationListView.as_view(),          name="application-list"),
    path("applications/<int:pk>/",              ApplicationDetailView.as_view(),        name="application-detail"),
    path("applications/<int:pk>/status/",       ApplicationStatusUpdateView.as_view(),  name="application-status"),
    path("applications/<int:pk>/withdraw/",     ApplicationWithdrawView.as_view(),      name="application-withdraw"),

    # ── Favoris ───────────────────────────────────────────────────────────
    path("favorites/",                          FavoriteJobListView.as_view(),          name="favorite-list"),
    path("jobs/<int:job_id>/favorite/",         FavoriteJobToggleView.as_view(),        name="favorite-toggle"),
]
