from django.urls import path

from .identify import IdentifyView

urlpatterns = [
    path("identify/", IdentifyView.as_view(), name="identify"),
]
