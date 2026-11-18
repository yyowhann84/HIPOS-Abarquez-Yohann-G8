from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import UserProfile
from accounts.utils import role_for
from .decorators import role_required
from .forms import AreaAssignmentForm, CleanupAreaForm, EventForm, ReviewForm, SubmissionEvidenceForm
from .models import AreaAssignment, CleanupArea, CleanupSubmission, Event, PhotoEvidence, Review, WasteRecord


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    role = role_for(request.user)
    if role == UserProfile.Role.ORGANIZER:
        return redirect("organizer_dashboard")
    if role == UserProfile.Role.REVIEWER:
        return redirect("reviewer_dashboard")
    return redirect("member_dashboard")


@role_required(UserProfile.Role.ORGANIZER)
def organizer_dashboard(request):
    events = Event.objects.all() if request.user.is_superuser else Event.objects.filter(created_by=request.user)
    events = events.annotate(area_count=Count("areas", distinct=True)).order_by("-event_date")
    context = {
        "events": events[:8],
        "total_events": events.count(),
        "total_areas": CleanupArea.objects.count() if request.user.is_superuser else CleanupArea.objects.filter(event__created_by=request.user).count(),
        "pending_reviews": CleanupSubmission.objects.filter(status=CleanupSubmission.Status.SUBMITTED).count(),
        "completed_areas": CleanupSubmission.objects.filter(status=CleanupSubmission.Status.COMPLETED).count(),
    }
    return render(request, "core/organizer_dashboard.html", context)


@role_required(UserProfile.Role.CLEANUP_MEMBER)
def member_dashboard(request):
    assigned_areas = CleanupArea.objects.filter(assignments__member=request.user).select_related("event").distinct()
    submissions = CleanupSubmission.objects.filter(member=request.user).select_related("area", "area__event")
    context = {
        "assigned_areas": assigned_areas,
        "submissions": submissions[:10],
        "open_events": Event.objects.filter(status=Event.Status.OPEN).order_by("event_date")[:6],
        "in_progress_count": submissions.filter(status=CleanupSubmission.Status.IN_PROGRESS).count(),
        "needs_cleanup_count": submissions.filter(status=CleanupSubmission.Status.NEEDS_CLEANUP).count(),
    }
    return render(request, "core/member_dashboard.html", context)


@role_required(UserProfile.Role.REVIEWER)
def reviewer_dashboard(request):
    pending = CleanupSubmission.objects.filter(status=CleanupSubmission.Status.SUBMITTED).select_related(
        "member", "area", "area__event"
    ).prefetch_related("photos", "waste_records")
    context = {
        "pending_submissions": pending,
        "pending_count": pending.count(),
        "completed_count": CleanupSubmission.objects.filter(status=CleanupSubmission.Status.COMPLETED).count(),
        "needs_cleanup_count": CleanupSubmission.objects.filter(status=CleanupSubmission.Status.NEEDS_CLEANUP).count(),
    }
    return render(request, "core/reviewer_dashboard.html", context)


@login_required
def event_list(request):
    events = Event.objects.all()
    if role_for(request.user) != UserProfile.Role.ORGANIZER and not request.user.is_superuser:
        events = events.exclude(status=Event.Status.DRAFT)
    selected_status = request.GET.get("status", "")
    if selected_status in dict(Event.Status.choices):
        events = events.filter(status=selected_status)
    return render(request, "core/event_list.html", {"events": events, "selected_status": selected_status, "status_choices": Event.Status.choices})


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event.objects.prefetch_related("areas__assignments__member", "areas__submissions"), pk=pk)
    if event.status == Event.Status.DRAFT and role_for(request.user) != UserProfile.Role.ORGANIZER and not request.user.is_superuser:
        raise PermissionDenied("This event is not published yet.")
    return render(request, "core/event_detail.html", {"event": event})


@role_required(UserProfile.Role.ORGANIZER)
def event_create(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.created_by = request.user
        event.save()
        messages.success(request, "Event created. You can now add cleanup areas and assign members.")
        return redirect("event_detail", pk=event.pk)
    return render(request, "core/event_form.html", {"form": form, "page_title": "Create event", "submit_label": "Create event"})


@role_required(UserProfile.Role.ORGANIZER)
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not request.user.is_superuser and event.created_by_id != request.user.id:
        raise PermissionDenied("You can only edit events you created.")
    form = EventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event details updated.")
        return redirect("event_detail", pk=event.pk)
    return render(request, "core/event_form.html", {"form": form, "page_title": "Edit event", "submit_label": "Save changes", "event": event})


@role_required(UserProfile.Role.ORGANIZER)
def area_create(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    if not request.user.is_superuser and event.created_by_id != request.user.id:
        raise PermissionDenied("You can only manage cleanup areas for events you created.")
    form = CleanupAreaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        area = form.save(commit=False)
        area.event = event
        area.save()
        messages.success(request, "Cleanup area created. Assign members from the area page.")
        return redirect("area_detail", pk=area.pk)
    return render(request, "core/area_form.html", {"form": form, "event": event, "page_title": "Add cleanup area"})


@login_required
def area_detail(request, pk):
    area = get_object_or_404(CleanupArea.objects.select_related("event"), pk=pk)
    can_manage = request.user.is_superuser or (
        role_for(request.user) == UserProfile.Role.ORGANIZER and area.event.created_by_id == request.user.id
    )
    if request.method == "POST":
        if not can_manage:
            raise PermissionDenied("Only the event organizer can change area assignments.")
        form = AreaAssignmentForm(request.POST)
        if form.is_valid():
            chosen = list(form.cleaned_data["members"])
            chosen_ids = {member.pk for member in chosen}
            AreaAssignment.objects.filter(area=area).exclude(member_id__in=chosen_ids).delete()
            for member in chosen:
                AreaAssignment.objects.get_or_create(area=area, member=member, defaults={"assigned_by": request.user})
            messages.success(request, "Area assignments saved.")
            return redirect("area_detail", pk=area.pk)
    else:
        form = AreaAssignmentForm(initial={"members": list(area.assignments.values_list("member_id", flat=True))})
    context = {
        "area": area,
        "form": form,
        "can_manage": can_manage,
        "is_assigned": AreaAssignment.objects.filter(area=area, member=request.user).exists(),
        "submissions": area.submissions.select_related("member"),
    }
    return render(request, "core/area_detail.html", context)


@role_required(UserProfile.Role.CLEANUP_MEMBER)
@require_POST
def start_cleanup(request, pk):
    area = get_object_or_404(CleanupArea.objects.select_related("event"), pk=pk)
    if not AreaAssignment.objects.filter(area=area, member=request.user).exists():
        messages.error(request, "You must be assigned to this area before starting cleanup.")
        return redirect("area_detail", pk=area.pk)
    submission, created = CleanupSubmission.objects.get_or_create(
        area=area, member=request.user, defaults={"status": CleanupSubmission.Status.IN_PROGRESS, "started_at": timezone.now()}
    )
    if not created:
        if submission.status in (CleanupSubmission.Status.SUBMITTED, CleanupSubmission.Status.COMPLETED):
            messages.info(request, "This cleanup has already been submitted or completed.")
            return redirect("submission_detail", pk=submission.pk)
        submission.status = CleanupSubmission.Status.IN_PROGRESS
        submission.submitted_at = None
        if not submission.started_at:
            submission.started_at = timezone.now()
        submission.save()
    messages.success(request, "Cleanup started. Add your notes, waste estimate, and photo evidence.")
    return redirect("submission_page", pk=submission.pk)


@role_required(UserProfile.Role.CLEANUP_MEMBER)
def submission_page(request, pk):
    submission = get_object_or_404(CleanupSubmission.objects.select_related("area", "area__event"), pk=pk, member=request.user)
    if not AreaAssignment.objects.filter(area=submission.area, member=request.user).exists():
        raise PermissionDenied("You are not assigned to this cleanup area.")
    if submission.status in (CleanupSubmission.Status.SUBMITTED, CleanupSubmission.Status.COMPLETED):
        messages.info(request, "This submission is locked while it is under review or completed.")
        return redirect("submission_detail", pk=submission.pk)
    form = SubmissionEvidenceForm(request.POST or None, request.FILES or None, initial={"notes": submission.notes})
    if request.method == "POST" and form.is_valid():
        action = request.POST.get("action", "save")
        if action == "submit" and not submission.photos.exists() and not form.cleaned_data.get("photo"):
            form.add_error("photo", "Upload at least one photo before submitting for review.")
        if form.is_valid():
            submission.notes = form.cleaned_data["notes"]
            if submission.status == CleanupSubmission.Status.NEEDS_CLEANUP:
                submission.status = CleanupSubmission.Status.IN_PROGRESS
                submission.submitted_at = None
            if not submission.started_at:
                submission.started_at = timezone.now()
            if action == "submit":
                submission.status = CleanupSubmission.Status.SUBMITTED
                submission.submitted_at = timezone.now()
            submission.save()
            category = form.cleaned_data.get("waste_category")
            quantity = form.cleaned_data.get("estimated_quantity")
            if category and quantity is not None:
                WasteRecord.objects.update_or_create(
                    submission=submission,
                    category=category,
                    defaults={
                        "estimated_quantity": quantity,
                        "unit": form.cleaned_data.get("unit") or "bags",
                        "notes": form.cleaned_data.get("waste_notes", ""),
                    },
                )
            photo = form.cleaned_data.get("photo")
            if photo:
                PhotoEvidence.objects.create(
                    submission=submission,
                    image=photo,
                    caption=form.cleaned_data.get("caption", ""),
                    uploaded_by=request.user,
                )
            if action == "submit":
                messages.success(request, "Cleanup submitted for reviewer verification.")
                return redirect("submission_detail", pk=submission.pk)
            messages.success(request, "Progress saved.")
            return redirect("submission_page", pk=submission.pk)
    return render(request, "core/submission_form.html", {"form": form, "submission": submission})


@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(
        CleanupSubmission.objects.select_related("member", "area", "area__event").prefetch_related("photos", "waste_records", "reviews__reviewer"),
        pk=pk,
    )
    allowed = (
        request.user.is_superuser
        or role_for(request.user) in (UserProfile.Role.ORGANIZER, UserProfile.Role.REVIEWER)
        or submission.member_id == request.user.id
        or AreaAssignment.objects.filter(area=submission.area, member=request.user).exists()
    )
    if not allowed:
        raise PermissionDenied("You cannot view this submission.")
    return render(request, "core/submission_detail.html", {"submission": submission})


@role_required(UserProfile.Role.REVIEWER)
@require_POST
def review_submission(request, pk):
    submission = get_object_or_404(CleanupSubmission, pk=pk)
    if submission.status != CleanupSubmission.Status.SUBMITTED:
        messages.error(request, "Only submissions awaiting review can be reviewed.")
        return redirect("reviewer_dashboard")
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.submission = submission
        review.reviewer = request.user
        review.save()
        if review.decision == Review.Decision.APPROVED:
            submission.status = CleanupSubmission.Status.COMPLETED
            messages.success(request, "Cleanup approved and marked completed.")
        else:
            submission.status = CleanupSubmission.Status.NEEDS_CLEANUP
            submission.submitted_at = None
            messages.warning(request, "Cleanup marked as needing more work. The assigned member can update and resubmit it.")
        submission.save()
        return redirect("submission_detail", pk=submission.pk)
    messages.error(request, "Please choose a valid review decision.")
    return redirect("submission_detail", pk=submission.pk)
