from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from demo.settings import BASE_URL
import helpers
import helpers.billing
from subscriptions.models import SubscriptionPrice, Subscription, UserSubscription
from django.contrib.auth import get_user_model
# Create your views here.

User = get_user_model()

def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subs_price_id'] = price_id
    return redirect("stripe-checkout-start")

@login_required
def checkout_redirect_view(request):
    checkout_price_id = request.session.get("checkout_subs_price_id")
    try:
        obj = SubscriptionPrice.objects.get(id=checkout_price_id)
    except:
        obj = None
    print(checkout_price_id)
    if checkout_price_id is None or obj is None:
        return redirect("pricing")
    customer_stripe_id = request.user.customer.stripe_id
    url_base = BASE_URL
    success_url_path = reverse("stripe-checkout-end")
    success_url = f"{url_base}{success_url_path}"
    pricing_url_path = reverse("pricing")
    cancel_url = f"{url_base}{pricing_url_path}"
    url = helpers.billing.start_checkout_session(
        customer_stripe_id,
        success_url=success_url,
        cancel_url=cancel_url,
        price_stripe_id=obj.stripe_id,
        raw=False
    )
    return redirect(url)

def checkout_finalize_view(request):
    session_id = request.GET.get('session_id')
    data = helpers.billing.get_checkout_customer_plan(session_id)
    price_stripe_id = data.pop("plan_id")
    customer_id = data.pop("customer_id")
    sub_stripe_id = data.pop("sub_price_id")
    subscription_data = {**data}
    try:
        sub_obj = Subscription.objects.get(subscriptionprice__stripe_id=price_stripe_id)
    except:
        sub_obj = None
    _user_sub_exists = False
    _sub_options = {
        "subcription":sub_obj,
        "stripe_id" : sub_stripe_id,
        "user_cancelled" : False,
        **subscription_data
    }
    try:
        user_obj = User.objects.get(customer__stripe_id=customer_id)
        _user_sub_exists = True
    except:
        user_obj = None
    try:
        _user_sub_obj = UserSubscription.objects.get(user=user_obj)
    except UserSubscription.DoesNotExist:
        _user_sub_obj = UserSubscription.objects.create(
            user=user_obj, 
            **_sub_options)
    except:
        _user_sub_obj = None
    
    if None in [sub_obj, user_obj, _user_sub_obj]:
        return HttpResponseBadRequest("Error with your account!")
    
    if _user_sub_exists:
        old_stripe_id = _user_sub_obj.stripe_id
        if old_stripe_id is not None:
            helpers.billing.cancel_subscription(old_stripe_id, reason="New Membership")
        for k,v in _sub_options.items():
            setattr(_user_sub_obj, k, v)
        _user_sub_obj.save()
    
    context = {}
    return render(request, "checkout/success.html", context)

    