# Generated by Django 3.1.2 on 2021-03-03 11:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import payments.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pool', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.FloatField(default=5)),
                ('paidBy', models.CharField(default='Jamiie Account', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ServerStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeStamp', models.DateTimeField(auto_now_add=True)),
                ('ram', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.CharField(max_length=20)),
                ('paidTime', models.DateTimeField(auto_now_add=True)),
                ('transactionUrl', models.CharField(max_length=255, unique=True)),
                ('transactionStatus', models.BooleanField(default=False)),
                ('lateTransactionStatus', models.BooleanField(default=False)),
                ('payDate', models.DateTimeField(blank=True, null=True)),
                ('loanPayment', models.BooleanField(default=False)),
                ('phone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('poolId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pool.createpool')),
            ],
        ),
        migrations.CreateModel(
            name='NotPaid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.CharField(max_length=20)),
                ('payDate', models.DateTimeField(blank=True, null=True)),
                ('uniqueId', models.CharField(max_length=20, unique=True)),
                ('paid', models.BooleanField(default=False)),
                ('phone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('poolId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pool.createpool')),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('transactionId', models.CharField(max_length=20, unique=True)),
                ('paid', models.BooleanField(default=False)),
                ('approved', models.BooleanField(default=False)),
                ('declined', models.BooleanField(default=False)),
                ('phone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('poolId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pool.createpool')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customerUrl', models.CharField(max_length=255, unique=True)),
                ('documentUrl', models.CharField(max_length=255, null=True, unique=True)),
                ('funding_src', models.CharField(max_length=255, null=True, unique=True)),
                ('document', models.ImageField(upload_to=payments.models.upload_document_to)),
                ('documentType', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
