# Generated by Django 4.2.13 on 2024-08-31 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='姓名')),
                ('email', models.EmailField(max_length=50, verbose_name='邮箱')),
                ('message', models.TextField(verbose_name='留言')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '联系我们',
                'verbose_name_plural': '联系我们',
                'db_table': 'contact',
            },
        ),
    ]