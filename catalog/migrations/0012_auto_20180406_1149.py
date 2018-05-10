# Generated by Django 2.0.2 on 2018-04-06 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0011_auto_20180406_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyinstance',
            name='request_status',
            field=models.CharField(choices=[('p', 'Pending'), ('a', 'Accepted'), ('d', 'Denied')], default='p', max_length=1, verbose_name='Request status'),
        ),
    ]
