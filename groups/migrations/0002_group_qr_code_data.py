# Generated by Django 4.2.7 on 2025-04-06 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='qr_code_data',
            field=models.BinaryField(blank=True, null=True, verbose_name='二维码图片数据'),
        ),
    ]
