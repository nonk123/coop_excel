from django.urls import path
from django.shortcuts import render

urlpatterns = [
    path('', lambda req: render(req, "coop_excel/index.html"), name="index"),
]
