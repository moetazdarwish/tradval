# Generated by Django 4.0 on 2023-04-04 23:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tradval', '0006_alter_companyevaluation_ref_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyactivity',
            name='evaluation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tradval.companyevaluation'),
        ),
        migrations.AlterField(
            model_name='companyactivity',
            name='reviews',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tradval.companyreviews'),
        ),
    ]