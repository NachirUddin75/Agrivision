from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("soil", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name="soilanalysis", name="user",
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name="soil_analyses"),
        ),
    ]
