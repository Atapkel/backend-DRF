from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

@shared_task
def send_congrats_email(username, user_email):
    subject = "Congrats!"
    message = (
        f'Hello {username}, our club management team congratulates you,\n'
        f'We believe you will be active in student life at SDU University.\n'
        f'We are happy to see you in our community!'
    )
    print(user_email)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,  # Better to use DEFAULT_FROM_EMAIL
        recipient_list=[user_email],
        fail_silently=False,
    )
