from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")

class SignUpForm(forms.ModelForm):
    """User sign‑up form with strong‑password and unique‑username checks."""

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="At least 8 chars with upper, lower & number."
    )
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email")

    # ---- field‑level validation ----
    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        return username

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        if not PASSWORD_REGEX.match(password):
            raise ValidationError(
                "Password must be ≥8 chars and include uppercase, lowercase and digit"
            )
        return password

    # ---- cross‑field validation ----
    def clean(self):
        cleaned_data = super().clean()
        p1, p2 = cleaned_data.get("password1"), cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords don’t match")
        return cleaned_data

    # ---- create user ----
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user