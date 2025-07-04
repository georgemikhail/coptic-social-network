# Generated by Django 4.2.7 on 2025-06-13 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Diocese',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('bishop_name', models.CharField(blank=True, max_length=200, null=True)),
                ('bishop_title', models.CharField(blank=True, max_length=100, null=True)),
                ('bishop_photo', models.ImageField(blank=True, null=True, upload_to='bishops/')),
                ('address', models.TextField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('country', models.CharField(max_length=100)),
                ('state_province', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Diocese',
                'verbose_name_plural': 'Dioceses',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Parish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('priest_name', models.CharField(blank=True, max_length=200, null=True)),
                ('priest_title', models.CharField(blank=True, max_length=100, null=True)),
                ('priest_photo', models.ImageField(blank=True, null=True, upload_to='priests/')),
                ('deacons', models.TextField(blank=True, help_text='List of deacons (one per line)', null=True)),
                ('address', models.TextField()),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='parishes/covers/')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='parishes/logos/')),
                ('service_schedule', models.JSONField(blank=True, default=dict, help_text='Weekly service schedule in JSON format')),
                ('facebook_page', models.URLField(blank=True, null=True)),
                ('youtube_channel', models.URLField(blank=True, null=True)),
                ('whatsapp_group', models.URLField(blank=True, null=True)),
                ('telegram_group', models.URLField(blank=True, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('timezone', models.CharField(default='UTC', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('allow_public_posts', models.BooleanField(default=True)),
                ('allow_member_posts', models.BooleanField(default=True)),
                ('require_admin_approval', models.BooleanField(default=False)),
                ('enable_donations', models.BooleanField(default=False)),
                ('donation_goal', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('donation_description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Parish',
                'verbose_name_plural': 'Parishes',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ParishEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('is_all_day', models.BooleanField(default=False)),
                ('location', models.CharField(blank=True, max_length=200, null=True)),
                ('event_type', models.CharField(choices=[('service', 'Church Service'), ('meeting', 'Meeting'), ('social', 'Social Event'), ('education', 'Educational'), ('youth', 'Youth Event'), ('charity', 'Charity Event'), ('other', 'Other')], default='other', max_length=50)),
                ('requires_registration', models.BooleanField(default=False)),
                ('max_attendees', models.PositiveIntegerField(blank=True, null=True)),
                ('registration_deadline', models.DateTimeField(blank=True, null=True)),
                ('is_public', models.BooleanField(default=True)),
                ('event_image', models.ImageField(blank=True, null=True, upload_to='events/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Parish Event',
                'verbose_name_plural': 'Parish Events',
                'ordering': ['start_datetime'],
            },
        ),
    ]
