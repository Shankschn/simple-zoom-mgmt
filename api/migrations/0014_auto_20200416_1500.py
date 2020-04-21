# Generated by Django 2.2.10 on 2020-04-16 07:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20200416_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Host', to_field='account', verbose_name='主持人'),
        ),
    ]
