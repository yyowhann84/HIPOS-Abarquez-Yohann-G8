from django.contrib import admin

from .models import AreaAssignment, CleanupArea, CleanupSubmission, Event, PhotoEvidence, Review, WasteCategory, WasteRecord


class CleanupAreaInline(admin.TabularInline):
    model = CleanupArea
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date", "venue", "status", "created_by")
    list_filter = ("status", "event_date")
    search_fields = ("title", "venue", "created_by__username")
    inlines = (CleanupAreaInline,)


@admin.register(CleanupArea)
class CleanupAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "location_notes", "created_at")
    list_filter = ("event__status",)
    search_fields = ("name", "event__title")


@admin.register(AreaAssignment)
class AreaAssignmentAdmin(admin.ModelAdmin):
    list_display = ("area", "member", "assigned_by", "assigned_at")
    list_filter = ("area__event",)
    search_fields = ("area__name", "member__username")


@admin.register(WasteCategory)
class WasteCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name",)


class WasteRecordInline(admin.TabularInline):
    model = WasteRecord
    extra = 0


class PhotoEvidenceInline(admin.TabularInline):
    model = PhotoEvidence
    extra = 0
    readonly_fields = ("uploaded_at",)


@admin.register(CleanupSubmission)
class CleanupSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "area", "member", "status", "submitted_at", "updated_at")
    list_filter = ("status", "area__event")
    search_fields = ("area__name", "member__username", "area__event__title")
    inlines = (WasteRecordInline, PhotoEvidenceInline)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("submission", "reviewer", "decision", "reviewed_at")
    list_filter = ("decision", "reviewed_at")
    search_fields = ("submission__area__name", "reviewer__username", "comments")


@admin.register(WasteRecord)
class WasteRecordAdmin(admin.ModelAdmin):
    list_display = ("submission", "category", "estimated_quantity", "unit", "created_at")
    list_filter = ("category",)
