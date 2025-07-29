from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms  import SignUpForm
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    # clear success/info messages that leaked from other pages
    if request.method == "GET":
        storage = messages.get_messages(request)
        error_only = [m for m in storage if 'error' in m.tags]
        for m in error_only:                     # re-queue only errors
            messages.add_message(request, m.level, m.message, extra_tags=m.tags)

    if request.method == "POST":
        identity = request.POST.get("username", "").strip()
        pwd      = request.POST.get("password", "")
        # map email → username
        if "@" in identity:
            try:
                identity = User.objects.get(email__iexact=identity).username
            except User.DoesNotExist:
                messages.error(request, "Invalid e-mail / password")
                return redirect("login")

        user = authenticate(request, username=identity, password=pwd)
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username/e-mail or password")
        return redirect("login")

    return render(request, "login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created – please log in.")
            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "register.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    # we don't need a success banner on login screen
    return redirect("login")


# ── DASHBOARD ───────────────────────────────────────
@login_required
def home_view(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        desc  = request.POST.get("description", "").strip()
        if title and desc:
            Project.objects.create(owner=request.user,
                                   title=title, description=desc)
            messages.success(request, "Project added.")
        else:
            messages.error(request, "Both fields are required.")
        return redirect("home")

    projects = Project.objects.filter(owner=request.user).order_by("-created_at")
    return render(request, "home.html", {"projects": projects})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST":
        project.delete()
        messages.info(request, "Project removed.")
    return redirect("home")


# ── REQUIREMENTS ────────────────────────────────────

from django.contrib.auth.decorators import login_required


@login_required
def requirement_view(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    reqs = Requirement.objects.filter(project=project).order_by("-created_at")
    edit = None

    # ----- POST handler -----
    if request.method == "POST":
        if request.POST.get("update_req"):  # update case
            req_pk = request.POST.get("req_pk")
            req = get_object_or_404(Requirement, pk=req_pk, project=project)
            req.req_id = request.POST.get("req_id").strip()
            req.name = request.POST.get("req_name").strip()
            req.description = request.POST.get("req_desc").strip()
            req.save()
        elif request.POST.get("add_req"):  # add case
            Requirement.objects.create(
                project=project,
                req_id=request.POST["req_id"].strip(),
                name=request.POST["req_name"].strip(),
                description=request.POST["req_desc"].strip()
            )
        return redirect("requirements", pk=pk)

    # ----- GET handler (edit mode) -----
    if request.GET.get("edit"):
        try:
            edit = Requirement.objects.get(pk=request.GET["edit"], project=project)
        except Requirement.DoesNotExist:
            edit = None

    return render(request, "requirements.html", {
        "project": project,
        "reqs": reqs,
        "edit": edit
    })
# Delete view
@login_required
def req_delete(request, pk, req_pk):
    req = get_object_or_404(Requirement, pk=req_pk, project__pk=pk, project__owner=request.user)
    req.delete()
    messages.success(request, "Requirement deleted successfully.")
    return redirect("requirements", pk=pk)




# Remove TESTCASE_DATA = [] (we're using database now)

from .models import Project, Requirement, TestCase

import openpyxl
from django.http import HttpResponse
from decimal import Decimal


# Remove TESTCASE_DATA = [] (we're using database now)

@login_required
def testcase_view(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    requirements = Requirement.objects.filter(project=project)
    testcases = TestCase.objects.filter(requirement__project=project)

    edit_pk = request.GET.get('edit')
    edit = None
    if edit_pk:
        try:
            edit = TestCase.objects.get(pk=edit_pk, requirement__project=project)
        except TestCase.DoesNotExist:
            pass

    if request.method == "POST":
        # Handle add
        if "add_testcase" in request.POST:
            requirement_id = request.POST.get("requirement_id")
            test_id = request.POST.get("test_id").strip()
            test_name = request.POST.get("test_name").strip()
            pre_condition = request.POST.get("pre_condition", "").strip()
            test_condition = request.POST.get("test_condition", "").strip()
            expected_result = request.POST.get("expected_result", "").strip()
            actual_result = request.POST.get("actual_result", "").strip()

            req = get_object_or_404(Requirement, pk=requirement_id, project=project)

            TestCase.objects.create(
                requirement=req,
                test_id=test_id,
                test_name=test_name,
                pre_condition=pre_condition,
                test_condition=test_condition,
                expected_result=expected_result,
                actual_result=actual_result
            )
            messages.success(request, "Test case added successfully!")
            return redirect("testcases", pk=pk)

        # Handle update
        elif "update_testcase" in request.POST:
            tc_pk = request.POST.get("tc_pk")
            expected_result = request.POST.get("expected_result", "").strip()
            actual_result = request.POST.get("actual_result", "").strip()
            test_result = request.POST.get("test_result", "Pending")

            testcase = get_object_or_404(
                TestCase,
                pk=tc_pk,
                requirement__project=project
            )

            # Increment version by 0.1 (using Decimal to avoid float error)
            testcase.version = testcase.version + Decimal('0.1')

            testcase.expected_result = expected_result
            testcase.actual_result = actual_result
            testcase.test_result = test_result
            testcase.save()

            messages.success(request, "Test case updated successfully!")
            return redirect("testcases", pk=pk)

    return render(request, "testcase.html", {
        "project": project,
        "requirements": requirements,
        "testcases": testcases,
        "edit": edit
    })


@login_required
def testcase_delete(request, pk, tc_pk):
    testcase = get_object_or_404(
        TestCase,
        pk=tc_pk,
        requirement__project__pk=pk,
        requirement__project__owner=request.user
    )
    testcase.delete()
    messages.success(request, "Test case deleted successfully!")
    return redirect("testcases", pk=pk)


@login_required
def export_testcases(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    testcases = TestCase.objects.filter(requirement__project=project)

    # Create Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    # Add headers
    headers = [
        "Req ID", "Requirement", "Test ID", "Purpose",
        "Pre Condition", "Test Condition", "Expected Result",
        "Actual Result", "Status", "Version"
    ]
    ws.append(headers)

    # Add data
    for tc in testcases:
        ws.append([
            tc.requirement.req_id,
            tc.requirement.name,
            tc.test_id,
            tc.test_name,
            tc.pre_condition or "",
            tc.test_condition or "",
            tc.expected_result,
            tc.actual_result or "",
            tc.test_result,
            float(tc.version)  # Convert Decimal to float for Excel
        ])

    # Create HTTP response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f"attachment; filename={project.title.replace(' ', '_')}_TestCases.xlsx"
    wb.save(response)

    return response