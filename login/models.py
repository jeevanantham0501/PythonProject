# login/models.py
from django.db import models
from django.contrib.auth.models import User


class LoginUser(models.Model):
    """
    If you kept a separate table for manual‑password sign‑ups.
    (Most projects just use Django's built‑in User, so this
    class is optional; keep only if you still need it.)
    """
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    username   = models.CharField(max_length=150, unique=True)
    email      = models.EmailField(unique=True)
    password   = models.CharField(max_length=128)  # store hashed manually

    def __str__(self) -> str:
        return self.username


class Project(models.Model):
    """One card visible on the home dashboard."""
    owner       = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="projects"
    )
    title       = models.CharField(max_length=100)
    description = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class Requirement(models.Model):
    """A requirement row that belongs to a project."""
    project      = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="requirements"
    )
    req_id       = models.CharField("Req ID", max_length=20)
    name         = models.CharField(max_length=120)
    description  = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "req_id")  # Req‑ID unique per project

    def __str__(self) -> str:
        return f"{self.project.title} – {self.req_id}"


from django.db import models



class TestCase(models.Model):
    TEST_RESULT_CHOICES = [
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
        ('Pending', 'Pending'),
    ]

    requirement = models.ForeignKey(
        Requirement, on_delete=models.CASCADE, related_name="testcases"
    )
    test_id = models.CharField(max_length=50)
    test_name = models.CharField(max_length=200)
    pre_condition = models.TextField(blank=True, null=True)
    test_condition = models.TextField(blank=True, null=True)
    expected_result = models.TextField()
    actual_result = models.TextField(blank=True, null=True)
    test_result = models.CharField(
        max_length=10,
        choices=TEST_RESULT_CHOICES,
        default='Pending'
    )
    version = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("requirement", "test_id")

    def __str__(self):
        return f"{self.test_id} - {self.test_name}"