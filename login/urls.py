from django.urls import path
from . import views

urlpatterns = [

    # ── Auth ─────────────────────────────
# Add this to your existing urlpatterns list

    path("",              views.login_view,     name="login"),
    path("register/",     views.register_view,  name="register"),
    path("logout/",       views.logout_view,    name="logout"),

    # ── Dashboard (projects) ─────────────
    path("home/",         views.home_view,      name="home"),
    path("project/<int:pk>/delete/",
         views.project_delete,                  name="project_delete"),

    # ── Requirement list / CRUD ──────────
    path("project/<int:pk>/requirements/",
         views.requirement_view,                name="requirements"),
    path("project/<int:pk>/requirement/<int:req_pk>/delete/",
         views.req_delete,                      name="req_delete"),

    path("project/<int:pk>/testcases/", views.testcase_view, name="testcases"),
    path("project/<int:pk>/testcase/<int:tc_pk>/delete/",
         views.testcase_delete, name="testcase_delete"),
    path("project/<int:pk>/testcases/export/",
         views.export_testcases, name="export_testcases"),
]
