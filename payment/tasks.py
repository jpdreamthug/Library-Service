import stripe
from celery import shared_task
from django.conf import settings

from payment.models import Payment


@shared_task
def check_payment_expiration() -> None:
    payments = Payment.objects.filter(
        status="PENDING"
    )
    for payment in payments:
        try:
            session = stripe.checkout.Session.retrieve(
                payment.session_id
            )
        except stripe.error.InvalidRequestError as e:
            print(f"Invalid session: {e}")
        except Exception as e:
            print(e)

        if session.status == "expired":
            print(f"Found expired session: {session.id}")
            payment.status = Payment.Status.EXPIRED
