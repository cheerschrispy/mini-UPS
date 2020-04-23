# Generated by Django 3.0.2 on 2020-04-23 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_remove_package_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='owner',
            field=models.CharField(blank=True, max_length=100, verbose_name='owner name'),
        ),
        migrations.AlterField(
            model_name='package',
            name='trackingnum',
            field=models.IntegerField(),
        ),
    ]
