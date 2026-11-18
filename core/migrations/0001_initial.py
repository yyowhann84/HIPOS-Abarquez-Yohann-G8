from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("event_date", models.DateField()),
                ("venue", models.CharField(max_length=180)),
                ("details", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("open", "Open for Cleanup"), ("closed", "Closed")], default="draft", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="hipos_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["event_date", "title"]},
        ),
        migrations.CreateModel(
            name="CleanupArea",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("location_notes", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("event", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="areas", to="core.event")),
            ],
            options={"ordering": ["event__event_date", "name"]},
        ),
        migrations.CreateModel(
            name="AreaAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assigned_at", models.DateTimeField(auto_now_add=True)),
                ("area", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assignments", to="core.cleanuparea")),
                ("assigned_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="hipos_assignments_made", to=settings.AUTH_USER_MODEL)),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="area_assignments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["member__username"]},
        ),
        migrations.CreateModel(
            name="WasteCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("description", models.CharField(blank=True, max_length=220)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "waste categories"},
        ),
        migrations.CreateModel(
            name="CleanupSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("in_progress", "In Progress"), ("submitted_for_review", "Submitted for Review"), ("completed", "Completed"), ("needs_cleanup", "Needs Cleanup")], default="pending", max_length=24)),
                ("notes", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("area", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="core.cleanuparea")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="cleanup_submissions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="WasteRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("estimated_quantity", models.DecimalField(decimal_places=2, max_digits=9)),
                ("unit", models.CharField(default="bags", max_length=24)),
                ("notes", models.CharField(blank=True, max_length=240)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="waste_records", to="core.wastecategory")),
                ("submission", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="waste_records", to="core.cleanupsubmission")),
            ],
            options={"ordering": ["category__name"]},
        ),
        migrations.CreateModel(
            name="PhotoEvidence",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="evidence/%Y/%m/")),
                ("caption", models.CharField(blank=True, max_length=180)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("submission", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="photos", to="core.cleanupsubmission")),
                ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="hipos_photo_evidence", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-uploaded_at"]},
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("decision", models.CharField(choices=[("approved", "Approve Cleanup"), ("needs_cleanup", "Needs More Cleanup")], max_length=20)),
                ("comments", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField(auto_now_add=True)),
                ("reviewer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="hipos_reviews", to=settings.AUTH_USER_MODEL)),
                ("submission", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="core.cleanupsubmission")),
            ],
            options={"ordering": ["-reviewed_at"]},
        ),
        migrations.AddConstraint(
            model_name="areaassignment",
            constraint=models.UniqueConstraint(fields=("area", "member"), name="unique_area_member_assignment"),
        ),
        migrations.AddConstraint(
            model_name="cleanupsubmission",
            constraint=models.UniqueConstraint(fields=("area", "member"), name="unique_area_member_submission"),
        ),
        migrations.AddConstraint(
            model_name="wasterecord",
            constraint=models.UniqueConstraint(fields=("submission", "category"), name="unique_waste_category_per_submission"),
        ),
    ]
