# Generated by Django 4.2.1 on 2023-07-09 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_productgallery_options_product_sizes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_name',
            field=models.CharField(max_length=200),
        ),
    ]
