# Generated by Django 5.2.4 on 2025-07-15 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price_cents', models.PositiveIntegerField()),
                ('description', models.TextField()),
                ('stripe_price_id', models.CharField(max_length=255)),
            ],
        ),
    ]
