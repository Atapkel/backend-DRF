import logging
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task



# @shared_task
# def send_congrats_email(username, user_email):
#     subject = "Congrats!"
#     message = (
#         f'Hello {username}, our club management team congratulates you,\n'
#         f'We believe you will be active in student life at SDU University.\n'
#         f'We are happy to see you in our community!'
#     )
#     print(user_email)
#     send_mail(
#         subject=subject,
#         message=message,
#         from_email=settings.DEFAULT_FROM_EMAIL,  # Better to use DEFAULT_FROM_EMAIL
#         recipient_list=[user_email],
#         fail_silently=False,
#     )

logger = logging.getLogger(__name__)

@shared_task
def send_verification_email(username, code):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        user = User.objects.get(username=username)
        verification_link = reverse(
            'verify-email',
            kwargs={'username': username, 'code': code}
        )
        full_url = f"{settings.DOMAIN_NAME}{verification_link}"

        plain_message = (
            f"Please click the link to verify your email:\n{full_url}\n"
            f"You have 15 minutes to verify your email."
        )

        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h2 style="color: #4f46e5;">Welcome to CampusClubHub!</h2>
                <p style="font-size: 16px; color: #333;">Hello <strong>{user.username}</strong>,</p>
                <p style="font-size: 16px; color: #333;">
                    Please verify your email by clicking the button below. This link will expire in 15 minutes.
                </p>
                <p style="text-align: center; margin: 20px 0;">
                    <a href="{full_url}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Verify Email
                    </a>
                </p>
                <p style="font-size: 14px; color: #777;">
                    If you did not request this, please ignore this email.
                </p>
            </div>
        </body>
        </html>
        """

        send_mail(
            subject="Verify Your Email - CampusClubHub",
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message
        )

    except User.DoesNotExist:
        logger.error(f"User with username {username} does not exist.")
        return False

# celery -A store worker --loglevel=info --pool=solo
