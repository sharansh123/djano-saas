# Generated by Django 5.0.10 on 2025-01-04 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0012_alter_subscription_options_subscription_featured_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='features',
            field=models.TextField(blank=True, help_text='features', null=True),
        ),
    ]