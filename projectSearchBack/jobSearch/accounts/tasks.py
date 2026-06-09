from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

#  1. RÉINITIALISATION DU MOT DE PASSE

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_email: str, uid: str, token: str) -> None:
    try:
        reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
        subject = "Réinitialisation de votre mot de passe"
        text_message = render_to_string("emails/password_reset.txt", {"reset_url": reset_url})
        html_message = render_to_string("emails/password_reset.html", {"reset_url": reset_url})
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)

#  2. NOUVELLE CANDIDATURE (notification à l'entreprise)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_new_application_email(
    self, company_email, company_name, candidate_name, job_title, application_id
):
    try:
        dashboard_url = f"{settings.FRONTEND_URL}/dashboard/applications/{application_id}"
        subject = f"Nouvelle candidature pour : {job_title}"
        text_message = render_to_string("emails/new_application.txt", {
            "company_name": company_name, "candidate_name": candidate_name,
            "job_title": job_title, "dashboard_url": dashboard_url,
        })
        html_message = render_to_string("emails/new_application.html", {
            "company_name": company_name, "candidate_name": candidate_name,
            "job_title": job_title, "dashboard_url": dashboard_url,
        })
        send_mail(
            subject=subject, message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[company_email],
            html_message=html_message, fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)

#  3. CHANGEMENT DE STATUT (notification au candidat)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_application_status_email(
    self, candidate_email, candidate_name, job_title, company_name, new_status
):
    try:
        is_accepted = new_status == "accepted"
        subject = (
            f"Votre candidature pour « {job_title} » a été acceptée 🎉"
            if is_accepted
            else f"Votre candidature pour « {job_title} » n'a pas été retenue"
        )
        context = {
            "candidate_name": candidate_name, "job_title": job_title,
            "company_name": company_name, "is_accepted": is_accepted,
            "jobs_url": f"{settings.FRONTEND_URL}/jobs",
        }
        text_message = render_to_string("emails/application_status.txt", context)
        html_message = render_to_string("emails/application_status.html", context)
        send_mail(
            subject=subject, message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate_email],
            html_message=html_message, fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)

#  4. OFFRE SUR LE POINT D'EXPIRER (rappel à l'entreprise)

@shared_task
def send_deadline_reminders_task():
    """Envoie les rappels pour les offres expirant dans 3 jours. Planifier dans CELERY_BEAT_SCHEDULE."""
    from jobs.models import Job
    threshold = timezone.now().date() + timedelta(days=3)
    jobs_expiring = Job.objects.filter(
        status=Job.JobStatus.OPEN,
        deadline=threshold,
    ).select_related("company__user")
    for job in jobs_expiring:
        send_job_deadline_reminder.delay(
            company_email=job.company.user.email,
            company_name=job.company.company_name,
            job_title=job.title,
            job_id=job.id,
            days_left=3,
        )
