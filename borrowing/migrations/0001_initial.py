# Generated by Django 5.0.8 on 2024-08-14 16:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('book', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Borrowing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrow_date', models.DateField(auto_now_add=True)),
                ('expected_return_date', models.DateField()),
                ('actual_return_date', models.DateField(blank=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowings', to='book.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='borrowing',
            constraint=models.CheckConstraint(check=models.Q(('expected_return_date__gt', models.F('borrow_date'))), name='expected_return_after_borrow'),
        ),
        migrations.AddConstraint(
            model_name='borrowing',
            constraint=models.CheckConstraint(check=models.Q(('actual_return_date__gte', models.F('borrow_date')), ('actual_return_date__isnull', True), _connector='OR'), name='actual_return_after_borrow_or_null'),
        ),
    ]
