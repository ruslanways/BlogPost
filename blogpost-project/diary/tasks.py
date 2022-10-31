from django.core.mail import send_mail
from celery import shared_task


@shared_task()
def send_email_task(link_to_change_user, token, user_email):
    """Sends an email when the feedback form has been submitted."""
    send_mail(
            "Postways token recovery",
            f"Here are your new access token expires in 5 min."
            f"\n\n'access': {token}\n\n"
            "You can use it to change password by Post-request to: "
            f"{link_to_change_user}"
            "\n\nTherefore you could obtain new tokens pair by logging.",
            None,
            [user_email],
        )

