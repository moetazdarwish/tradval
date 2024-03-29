# Generated by Django 4.0 on 2023-04-05 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tradval', '0009_companyclaims_companyactivity_claim'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyclaims',
            name='company',
        ),
        migrations.AddField(
            model_name='companyclaims',
            name='claimer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='claimer', to='tradval.companydetail'),
        ),
        migrations.AddField(
            model_name='companyclaims',
            name='claimest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='claimest', to='tradval.companydetail'),
        ),
    ]
