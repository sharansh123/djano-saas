from pyexpat import model
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings

import helpers.billing
import stripe
# Create your models here.

User = settings.AUTH_USER_MODEL
ALLOW_CUSTOM_GROUP = True

SUBSCRIPTION_PERMISSIONS = [
            ("advanced", "Advanced Perm"),
            ("pro", "Pro Perm"),
            ("basic", "Basic Perm")
        ]

class Subscription(models.Model):
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission,
        limit_choices_to={
            "content_type__app_label": "subscriptions",
            "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]
        })
    stripe_id = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
    def save(self, *args, **kwargs):
        if not self.stripe_id:
            name = self.name
            stripe_id = helpers.billing.create_product(name=name, metadata={"subs_plan":self.id},raw=False)
            self.stripe_id = stripe_id
        
        super().save(*args,**kwargs)
    
    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
class SubscriptionPrice(models.Model):

    class IntervalChoices(models.TextChoices):
        MONTHLY = "month", "Monthly"
        YEARLY = "year", "Yearly"


    subscription= models.ForeignKey(Subscription,on_delete=models.SET_NULL, null=True)
    stripe_id= models.CharField(max_length=120, blank=True, null=True)
    interval = models.CharField(max_length=120, default=IntervalChoices.MONTHLY, choices=IntervalChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)


    @property
    def stripe_currency(self):
        return "usd"
    
    @property
    def stripe_price(self):
        return self.price * 100

    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id
    
    def save(self, *args, **kwargs):
        if(not self.stripe_id and self.product_stripe_id is not None):
            stripe_id = helpers.billing.create_price(
                currency=self.stripe_currency,
                unit_amount=self.stripe_price,
                interval=self.interval,
                product=self.product_stripe_id,
                metadata={"subs_plan_price":self.id},
                raw = False
            )
        self.stripe_id = stripe_id   
        super.save(*args, **kwargs)


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subcription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)


def user_post_save_signal(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    sub_obj = user_sub_instance.subcription#1
    grp_ids = []
    if sub_obj is not None:
        grp_obj = sub_obj.groups.all()
        grp_ids = grp_obj.values_list('id', flat=True)
    if not ALLOW_CUSTOM_GROUP:
        user.groups.set(grp_obj)
    else:
        sub_qs = Subscription.objects.filter(active=True)
        if sub_obj is not None:
            sub_qs = sub_qs.exclude(id=sub_obj.id)#2.3
        subs_grp = sub_qs.value_list("groups__id", flat=True)# c.d.e.f
        subs_grp_set = set(subs_grp)# c.d.e.f
        grp_ids = grp_obj.value_list('id', flat=True)#a.b
        current_grp = user.groups.all().value_list('id', flat=True)#a.b.c.g
        grp_ids_set = set(grp_ids)#a.b
        current_grp_set = set(current_grp) - subs_grp_set#a.b.c.g - c.d.e.f = a.b.g
        final_list = list(grp_ids_set | current_grp_set) #a.b.g
        user.groups.set(final_list)

post_save.connect(user_post_save_signal, sender=UserSubscription)
