from django.db import migrations, models
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recenseamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nim', models.CharField(max_length=20, unique=True, null=True, blank=True)),
                ('nome_completo', models.CharField(max_length=150)),
                ('filiacao_pai', models.CharField(max_length=150)),
                ('filiacao_mae', models.CharField(max_length=150)),
                ('data_nascimento', models.DateField()),
                ('nacionalidade', models.CharField(max_length=100)),
                ('naturalidade', models.CharField(max_length=100)),
                ('morada', models.CharField(max_length=200)),
                ('telefone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('contacto_familiar', models.CharField(max_length=150)),
                ('documento_identidade', models.FileField(upload_to='documentos_identidade/')),
                ('usuario', models.OneToOneField(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
