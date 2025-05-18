from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from tracking.models import Agent, Campaign
from mgmt.forms import CompanyForm
from tracking.forms import AgentForm
from django.contrib.auth.forms import AuthenticationForm
from mgmt.models import User


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    if not isinstance(request.user, User):
        return redirect('login')

    user: User = request.user

    return render(request, 'mgmt/dashboard.html', {'company': user.company})

@login_required
def edit_company_view(request: HttpRequest) -> HttpResponse:
    if not isinstance(request.user, User):
        return redirect('login')

    user: User = request.user
    form = CompanyForm(request.POST or None, instance=user.company)

    if request.method == 'POST' and form.is_valid():
        company = form.save()
        if user.company != company:
            user.company = company
            user.save()

        return redirect('dashboard')

    return render(request, 'mgmt/edit_company.html', {'form': form, 'company': user.company})

@login_required
def agent_list_view(request: HttpRequest) -> HttpResponse:
    if not isinstance(request.user, User):
        return redirect('login')

    user: User = request.user
    agents = Agent.objects.filter(campaign__company=user.company)

    return render(request, 'mgmt/agent_list.html', {'agents': agents})

@login_required
def agent_create_view(request: HttpRequest) -> HttpResponse:
    if not isinstance(request.user, User):
        return redirect('login')

    user: User = request.user
    form = AgentForm(request.POST or None)

    if form.is_bound:
        form.fields['campaign'].queryset = Campaign.objects.filter(company=user.company)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agent created successfully.')
        return redirect('agent_list')

    return render(request, 'mgmt/agent_form.html', {'form': form, 'title': 'Add Agent'})

@login_required
def agent_edit_view(request: HttpRequest, agent_id: int) -> HttpResponse:
    if not isinstance(request.user, User):
        return redirect('login')

    user: User = request.user
    agent = get_object_or_404(Agent, id=agent_id, campaign__company=user.company)
    form = AgentForm(request.POST or None, instance=agent)
    form.fields['campaign'].queryset = Campaign.objects.filter(company=user.company)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agent updated successfully.')
        return redirect('agent_list')

    return render(request, 'mgmt/agent_form.html', {'form': form, 'title': 'Edit Agent'})

def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        return redirect('dashboard')

    return render(request, 'mgmt/login.html', {'form': form})

def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)

    return redirect('home')
