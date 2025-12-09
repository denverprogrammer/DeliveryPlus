from __future__ import annotations
from dal import autocomplete
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from mgmt.forms import CompanyForm
from mgmt.forms import RecipientForm
from mgmt.models import Company
from mgmt.models import User
from taggit.models import Tag
from tracking.models import Recipient


# from tracking.models import Campaign
# from tracking.models import Tracking


@login_required
def dashboard_view(request: HttpRequest) -> JsonResponse:
    if not isinstance(request.user, User):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user: User = request.user
    if user.company:
        return JsonResponse({"company": {"name": user.company.name}})
    return JsonResponse({"company": {"name": "No Company"}})


@login_required
def edit_company_view(request: HttpRequest) -> JsonResponse:
    if not isinstance(request.user, User):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user: User = request.user

    if request.method == "GET":
        company_name = user.company.name if user.company else "No Company"
        return JsonResponse(
            {
                "company": {
                    "name": company_name,
                    # Add other company fields as needed
                }
            }
        )

    if request.method == "POST":
        form = CompanyForm(request.POST, instance=user.company)
        if form.is_valid():
            company = form.save()
            if user.company != company:
                user.company = company
                user.save()
            return JsonResponse({"success": True})
        return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def recipient_list_view(request: HttpRequest) -> JsonResponse:
    if not isinstance(request.user, User):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user: User = request.user
    recipients = Recipient.objects.filter(company=user.company)

    recipients_data = []
    for recipient in recipients:
        recipients_data.append(
            {
                "id": recipient.id,
                "first_name": recipient.first_name,
                "last_name": recipient.last_name,
                "email": recipient.email,
                "status": recipient.status,
            }
        )

    return JsonResponse({"recipients": recipients_data})


@login_required
def recipient_create_view(request: HttpRequest) -> JsonResponse:
    if not isinstance(request.user, User):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user: User = request.user

    if request.method == "POST":
        form = RecipientForm(request.POST)
        if hasattr(form.fields["company"], "queryset") and user.company:
            form.fields["company"].queryset = Company.objects.filter(id=user.company.id)
        elif hasattr(form.fields["company"], "queryset"):
            form.fields["company"].queryset = Company.objects.none()

        if form.is_valid():
            recipient = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "recipient": {
                        "id": recipient.id,
                        "first_name": recipient.first_name,
                        "last_name": recipient.last_name,
                        "email": recipient.email,
                        "status": recipient.status,
                    },
                }
            )
        return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def recipient_edit_view(request: HttpRequest, recipient_id: int) -> JsonResponse:
    if not isinstance(request.user, User):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user: User = request.user
    recipient = get_object_or_404(Recipient, id=recipient_id, company=user.company)

    if request.method == "GET":
        return JsonResponse(
            {
                "recipient": {
                    "id": recipient.id,
                    "first_name": recipient.first_name,
                    "last_name": recipient.last_name,
                    "email": recipient.email,
                    "phone_number": recipient.phone_number,
                    "status": recipient.status,
                }
            }
        )

    if request.method == "POST":
        form = RecipientForm(request.POST, instance=recipient)
        if hasattr(form.fields["company"], "queryset") and user.company:
            form.fields["company"].queryset = Company.objects.filter(id=user.company.id)
        elif hasattr(form.fields["company"], "queryset"):
            form.fields["company"].queryset = Company.objects.none()

        if form.is_valid():
            recipient = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "recipient": {
                        "id": recipient.id,
                        "first_name": recipient.first_name,
                        "last_name": recipient.last_name,
                        "email": recipient.email,
                        "status": recipient.status,
                    },
                }
            )
        return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def login_view(request: HttpRequest) -> JsonResponse:
    if request.user.is_authenticated:
        return JsonResponse({"error": "Already authenticated"}, status=400)

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({"success": True, "token": "session_token"})
        return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


def logout_view(request: HttpRequest) -> JsonResponse:
    logout(request)
    return JsonResponse({"success": True})


class CompanyTagAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self) -> QuerySet[Tag]:
        # Get company_id from URL parameters
        company_id = self.kwargs.get("company_id")

        # Start with all tags
        qs: QuerySet[Tag] = Tag.objects.all()

        # Filter by company if company_id is provided
        if company_id:
            # Get tags that are used by recipients belonging to this company
            qs = qs.filter(
                taggit_taggeditem_items__content_type__model="recipient",
                taggit_taggeditem_items__object_id__in=Recipient.objects.filter(
                    company_id=company_id
                ).values_list("id", flat=True),
            ).distinct()

        # Filter by search query if provided
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
