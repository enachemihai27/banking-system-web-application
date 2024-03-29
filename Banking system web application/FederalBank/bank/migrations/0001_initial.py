# Generated by Django 3.1.4 on 2021-05-05 21:05

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=200)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True)),
                ('company_name', models.CharField(blank=True, max_length=200)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('contract_start_date', models.DateField(blank=True, null=True)),
                ('contract_end_date', models.DateField(blank=True, null=True)),
                ('amount', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(999999999), django.core.validators.MinValueValidator(0)])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
