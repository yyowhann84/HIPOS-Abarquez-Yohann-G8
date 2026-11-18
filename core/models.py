from django.conf import settings
from django.db import models


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open for Cleanup"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=160)
    event_date = models.DateField()
    venue = models.CharField(max_length=180)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="hipos_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event_date", "title"]

    def __str__(self):
        return f"{self.title} ({self.event_date:%b %d, %Y})"


class CleanupArea(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="areas")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    location_notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["event__event_date", "name"]

    def __str__(self):
        return f"{self.event.title} — {self.name}"


class AreaAssignment(models.Model):
    area = models.ForeignKey(CleanupArea, on_delete=models.CASCADE, related_name="assignments")
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="area_assignments")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="hipos_assignments_made")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["member__username"]
        constraints = [models.UniqueConstraint(fields=["area", "member"], name="unique_area_member_assignment")]

    def __str__(self):
        return f"{self.member.username} → {self.area.name}"


class WasteCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=220, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "waste categories"

    def __str__(self):
        return self.name


class CleanupSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED = "submitted_for_review", "Submitted for Review"
        COMPLETED = "completed", "Completed"
        NEEDS_CLEANUP = "needs_cleanup", "Needs Cleanup"

    area = models.ForeignKey(CleanupArea, on_delete=models.CASCADE, related_name="submissions")
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cleanup_submissions")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [models.UniqueConstraint(fields=["area", "member"], name="unique_area_member_submission")]

    def __str__(self):
        return f"{self.area.name} — {self.member.username} ({self.get_status_display()})"


class WasteRecord(models.Model):
    submission = models.ForeignKey(CleanupSubmission, on_delete=models.CASCADE, related_name="waste_records")
    category = models.ForeignKey(WasteCategory, on_delete=models.PROTECT, related_name="waste_records")
    estimated_quantity = models.DecimalField(max_digits=9, decimal_places=2)
    unit = models.CharField(max_length=24, default="bags")
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__name"]
        constraints = [models.UniqueConstraint(fields=["submission", "category"], name="unique_waste_category_per_submission")]

    def __str__(self):
        return f"{self.category.name}: {self.estimated_quantity} {self.unit}"


class PhotoEvidence(models.Model):
    submission = models.ForeignKey(CleanupSubmission, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="evidence/%Y/%m/")
    caption = models.CharField(max_length=180, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="hipos_photo_evidence")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Evidence for {self.submission}"


class Review(models.Model):
    class Decision(models.TextChoices):
        APPROVED = "approved", "Approve Cleanup"
        NEEDS_CLEANUP = "needs_cleanup", "Needs More Cleanup"

    submission = models.ForeignKey(CleanupSubmission, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="hipos_reviews")
    decision = models.CharField(max_length=20, choices=Decision.choices)
    comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reviewed_at"]

    def __str__(self):
        return f"{self.get_decision_display()} — submission #{self.submission_id}"
