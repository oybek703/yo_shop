# Generated by Django 3.2.9 on 2021-12-15 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
