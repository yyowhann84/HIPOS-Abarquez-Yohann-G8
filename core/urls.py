from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("organizer/", views.organizer_dashboard, name="organizer_dashboard"),
    path("member/", views.member_dashboard, name="member_dashboard"),
    path("reviewer/", views.reviewer_dashboard, name="reviewer_dashboard"),
    path("events/", views.event_list, name="event_list"),
    path("events/create/", views.event_create, name="event_create"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/<int:pk>/edit/", views.event_update, name="event_update"),
    path("events/<int:event_pk>/areas/create/", views.area_create, name="area_create"),
    path("areas/<int:pk>/", views.area_detail, name="area_detail"),
    path("areas/<int:pk>/start/", views.start_cleanup, name="start_cleanup"),
    path("submissions/<int:pk>/work/", views.submission_page, name="submission_page"),
    path("submissions/<int:pk>/", views.submission_detail, name="submission_detail"),
    path("submissions/<int:pk>/review/", views.review_submission, name="review_submission"),
]
