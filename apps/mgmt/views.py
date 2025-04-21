from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from tracking.models import Agent, Campaign
from mgmt.forms import CompanyForm
from tracking.forms import AgentForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import AuthenticationForm


@login_required
def dashboard_view(request):
    return render(request, 'mgmt/dashboard.html', {'company': request.user.company})

@login_required
def edit_company_view(request):
    company = request.user.company  # Use the company from the logged-in user
    form = CompanyForm(request.POST or None, instance=company)

    if request.method == 'POST' and form.is_valid():
        company = form.save()
        if request.user.company != company:
            request.user.company = company
            request.user.save()

        return redirect('dashboard')

    return render(request, 'mgmt/edit_company.html', {'form': form, 'company': company})

@login_required
def agent_list_view(request):
    agents = Agent.objects.filter(campaign__company=request.user.company)
    return render(request, 'mgmt/agent_list.html', {'agents': agents})

@login_required
def agent_create_view(request):
    form = AgentForm(request.POST or None)
    if form.is_bound:
        form.fields['campaign'].queryset = Campaign.objects.filter(company=request.user.company)

    if request.method == 'POST' and form.is_valid():
        agent = form.save()
        messages.success(request, 'Agent created successfully.')
        return redirect('agent_list')

    return render(request, 'mgmt/agent_form.html', {'form': form, 'title': 'Add Agent'})

@login_required
def agent_edit_view(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id, campaign__company=request.user.company)
    form = AgentForm(request.POST or None, instance=agent)
    form.fields['campaign'].queryset = Campaign.objects.filter(company=request.user.company)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agent updated successfully.')
        return redirect('agent_list')

    return render(request, 'mgmt/agent_form.html', {'form': form, 'title': 'Edit Agent'})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        return redirect('dashboard')

    return render(request, 'mgmt/login.html', {'form': form})

def logout_view(request):
    logout(request)

    return redirect('home')
