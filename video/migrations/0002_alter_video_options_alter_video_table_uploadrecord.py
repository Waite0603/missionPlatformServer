# Generated by Django 4.2.13 on 2024-08-29 10:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'verbose_name': '视频', 'verbose_name_plural': '视频'},
        ),
        migrations.AlterModelTable(
            name='video',
            table='video',
        ),
        migrations.CreateModel(
            name='UploadRecord',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('path', models.CharField(max_length=255)),
                ('format', models.CharField(max_length=255)),
                ('size', models.IntegerField()),
                ('upload_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=1)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '上传记录',
                'verbose_name_plural': '上传记录',
                'db_table': 'upload_record',
            },
        ),
    ]