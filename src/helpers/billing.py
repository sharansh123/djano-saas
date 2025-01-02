from decouple import config
import stripe

DJANGO_DEBUG = True#config('DEBUG', default=False, cast=bool)
STRIPE_SECRET_KEY = config('STRIPE_KEY', default="", cast=str)

if "sk_test" in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError("Invalid Stripe Key for prod")

stripe.api_key = STRIPE_SECRET_KEY

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