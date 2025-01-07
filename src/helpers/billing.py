from decouple import config
from helpers import date_utils
import stripe

DJANGO_DEBUG = True#config('DEBUG', default=False, cast=bool)
STRIPE_SECRET_KEY = config('STRIPE_KEY', default="", cast=str)

if "sk_test" in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError("Invalid Stripe Key for prod")

stripe.api_key = STRIPE_SECRET_KEY

def serialize_subs_data(sub_response):
    return {
        "current_period_start": date_utils.timestamp_as_datetime(sub_response.current_period_start),
        "current_period_end": date_utils.timestamp_as_datetime(sub_response.current_period_end),
        "status": sub_response.status
    }

def create_customer(name="", email="", metadata={}, raw=False):
    response = stripe.Customer.create(
        name=name,
        email=email,
        metadata=metadata
    )
    print("hello from stripe!")
    print(response)
    if raw:
        return response
    return response.id

def create_product(
        name="",
        metadata={},
        raw=False
):
    resp = stripe.Product.create(name=name,metadata=metadata)
    print(resp)
    if raw:
        return resp
    stripe_id = resp.id
    return stripe_id


def create_price(
        currency="usd",
                unit_amount="9999",
                interval="month",
                product=None,
                metadata={},
                raw = False
):
    if product is None:
        return None
    resp = stripe.Price.create(
                currency= currency,
                unit_amount=unit_amount,
                recurring={"interval": interval},
                product=product,
                metadata=metadata
            )
    print(resp)
    if raw:
        return resp
    stripe_id = resp.id
    return stripe_id

def start_checkout_session(customer_id, 
                           success_url="", 
                           price_stripe_id="", 
                           cancel_url = "", 
                           raw=True):
    if not success_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):
        success_url = f"{success_url}"+"?session_id={CHECKOUT_SESSION_ID}"
    response = stripe.checkout.Session.create(
        customer=customer_id,
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{"price": price_stripe_id, "quantity": 1}],
        mode="subscription",
        )
    print(response)
    if raw:
        return response
    return response.url

def get_checkout_session(session_id, raw=True):
    response = stripe.checkout.Session.retrieve(
  session_id)
    if raw:
        return response
    return response.url

def get_subscription(subs_id, raw=True):
    response = stripe.Subscription.retrieve(
  subs_id)
    if raw:
        return response
    return serialize_subs_data(response)

def get_checkout_customer_plan(session_id):
    response = get_checkout_session(session_id, raw=True)
    customer_id = response.customer
    sub_stripe_id = response.subscription
    sub_response = get_subscription(sub_stripe_id)
    sub_plan = sub_response.plan
    price_stripe_id = sub_plan.id
    sub_data = serialize_subs_data(sub_response)
    data = {
        "customer_id": customer_id,
        "plan_id": price_stripe_id,
        "sub_price_id": sub_stripe_id,
        **sub_data,
    }
    return data

def cancel_subscription(subs_id, reason="", feedback="other", raw=True):
    response = stripe.Subscription.cancel(
    subs_id,
    cancellation_details={
        "comment": reason,
        "feedback": feedback
    }
  )
    if raw:
        return response
    return response.url
    