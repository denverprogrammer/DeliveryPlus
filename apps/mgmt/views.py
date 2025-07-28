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
from mgmt.forms import AgentForm
from mgmt.forms import CompanyForm
from mgmt.models import User
from taggit.models import Tag
from tracking.models import Agent
from tracking.models import Campaign


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
def agent_list_view(request: HttpRequest) -> JsonResponse:
    if not isinstance(request.user, User):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user: User = request.user
    agents = Agent.objects.filter(campaign__company=user.company)

    agents_data = []
    for agent in agents:
        agents_data.append(
            {
                "id": agent.id,
                "first_name": agent.first_name,
                "last_name": agent.last_name,
                "email": agent.email,
                "status": agent.status,
            }
        )

    return JsonResponse({"agents": agents_data})


@login_required
def agent_create_view(request: HttpRequest) -> JsonResponse:
    if not isinstance(request.user, User):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user: User = request.user

    if request.method == "POST":
        form = AgentForm(request.POST)
        if hasattr(form.fields["campaign"], "queryset"):
            form.fields["campaign"].queryset = Campaign.objects.filter(company=user.company)

        if form.is_valid():
            agent = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "agent": {
                        "id": agent.id,
                        "first_name": agent.first_name,
                        "last_name": agent.last_name,
                        "email": agent.email,
                        "status": agent.status,
                    },
                }
            )
        return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def agent_edit_view(request: HttpRequest, agent_id: int) -> JsonResponse:
    if not isinstance(request.user, User):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user: User = request.user
    agent = get_object_or_404(Agent, id=agent_id, campaign__company=user.company)

    if request.method == "GET":
        return JsonResponse(
            {
                "agent": {
                    "id": agent.id,
                    "first_name": agent.first_name,
                    "last_name": agent.last_name,
                    "email": agent.email,
                    "phone_number": agent.phone_number,
                    "status": agent.status,
                }
            }
        )

    if request.method == "POST":
        form = AgentForm(request.POST, instance=agent)
        if hasattr(form.fields["campaign"], "queryset"):
            form.fields["campaign"].queryset = Campaign.objects.filter(company=user.company)

        if form.is_valid():
            agent = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "agent": {
                        "id": agent.id,
                        "first_name": agent.first_name,
                        "last_name": agent.last_name,
                        "email": agent.email,
                        "status": agent.status,
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
            # Get tags that are used by agents belonging to this company's campaigns
            qs = qs.filter(
                taggit_taggeditem_items__content_type__model="agent",
                taggit_taggeditem_items__object_id__in=Agent.objects.filter(
                    campaign__company_id=company_id
                ).values_list("id", flat=True),
            ).distinct()

        # Filter by search query if provided
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
