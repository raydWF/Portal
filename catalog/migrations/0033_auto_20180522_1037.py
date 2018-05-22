# Generated by Django 2.0.4 on 2018-05-22 14:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0032_remove_keyinstance_keyrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyinstance',
            name='date_returned',
            field=models.DateField(blank=True, null=True, verbose_name='Date to be returned'),
        ),
        migrations.AlterField(
            model_name='keyrequest',
            name='date_due_back',
            field=models.DateField(default=datetime.date(2018, 6, 5)),
        ),
    ]