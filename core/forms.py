from django import forms
from django.contrib.auth import get_user_model

from accounts.models import UserProfile
from .models import CleanupArea, Event, Review, WasteCategory

User = get_user_model()


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("title", "event_date", "venue", "details", "status")
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "details": forms.Textarea(attrs={"rows": 4}),
        }


class CleanupAreaForm(forms.ModelForm):
    class Meta:
        model = CleanupArea
        fields = ("name", "description", "location_notes")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class AreaAssignmentForm(forms.Form):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Assigned cleanup members",
        help_text="Only registered Cleanup Member accounts are listed.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["members"].queryset = User.objects.filter(
            is_active=True, profile__role=UserProfile.Role.CLEANUP_MEMBER
        ).order_by("first_name", "last_name", "username")


class SubmissionEvidenceForm(forms.Form):
    notes = forms.CharField(
        label="Cleanup notes",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Describe what was cleaned and any remaining issues."}),
    )
    waste_category = forms.ModelChoiceField(
        queryset=WasteCategory.objects.filter(is_active=True), required=False, label="Waste category"
    )
    estimated_quantity = forms.DecimalField(
        required=False, min_value=0.01, max_digits=9, decimal_places=2, label="Estimated quantity"
    )
    unit = forms.ChoiceField(
        required=False,
        choices=(("bags", "Bags"), ("kg", "Kilograms (kg)"), ("items", "Items"), ("liters", "Liters (L)")),
        initial="bags",
        label="Unit",
    )
    waste_notes = forms.CharField(required=False, max_length=240, label="Waste notes")
    photo = forms.ImageField(required=False, label="Photo evidence")
    caption = forms.CharField(required=False, max_length=180, label="Photo caption")

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get("waste_category")
        quantity = cleaned.get("estimated_quantity")
        if bool(category) != bool(quantity):
            raise forms.ValidationError("Select both a waste category and an estimated quantity, or leave both blank.")
        return cleaned


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("decision", "comments")
        widgets = {"comments": forms.Textarea(attrs={"rows": 4, "placeholder": "Explain the decision or what needs to be improved."})}
