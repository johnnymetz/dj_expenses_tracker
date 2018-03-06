from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from .models import Expense
from .forms import ExpenseForm, ProfileForm
from .helpers import sqlalchemy_objects_to_dicts, build_results
from . import constants as const


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)  # saves user's id in session
            messages.success(request, 'Registration successful. Welcome {}!'.format(user.username))
            return redirect(reverse('expenses:index'))
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)


@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    messages.success(request, "You've been successfully logged out")


@login_required
@require_http_methods(["GET", "POST"])
def index(request):
    query_list = request.user.expenses.all()
    if not query_list:
        messages.info(request, 'Please add an expense to get started!')
        return redirect(reverse('expenses:add_expense'))

    assert query_list
    user_expenses = sqlalchemy_objects_to_dicts(query_list)
    results = build_results(user_expenses, request.session)

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            # database validators satisfied
            profile_form.save()
            messages.success(request, 'Monthly limits successfully updated!')
        else:
            messages.error(request, 'Something went wrong...')
    else:
        profile_form = ProfileForm(instance=request.user.profile)

    context = {
        'profile_form': profile_form,
        'user_expenses': user_expenses,
        'results': results,
        'category_to_subcategory': const.CATEGORY_TO_SUBCATEGORY
    }
    return render(request, 'expenses/index.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense successfully added!')
        else:
            messages.error(request, 'Validation error.')
    else:
        form = ExpenseForm()

    pk_to_expense = {i.id: {'item': i.item,
                            'cost': i.cost,
                            'date_purchased': i.date_purchased,
                            'category': i.category,
                            'subcategory': i.subcategory} for i in Expense.objects.all()}
    context = {
        'expense_action': 'add',
        'form': form,
        'pk_to_expense': pk_to_expense,
        'categories': list(const.CATEGORY_TO_SUBCATEGORY.keys()),
        'category_to_subcategory': dict(const.CATEGORY_TO_SUBCATEGORY)
    }
    return render(request, 'expenses/single_expense.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_expense(request, expense_id):
    try:
        expense = Expense.objects.get(pk=expense_id)
    except Expense.DoesNotExist:
        messages.warning(request, 'Expense does not exist.')
        return redirect(reverse('expenses:index'))

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense successfully updated!')
        else:
            messages.error(request, 'Validation error.')
    else:
        form = ExpenseForm(instance=expense)

    pk_to_expense = {i.id: {'item': i.item,
                            'cost': i.cost,
                            'date_purchased': i.date_purchased,
                            'category': i.category,
                            'subcategory': i.subcategory} for i in Expense.objects.all()}
    context = {
        'expense_action': 'edit',
        'expense': expense,
        'form': form,
        'pk_to_expense': pk_to_expense,
        'categories': list(const.CATEGORY_TO_SUBCATEGORY.keys()),
        'category_to_subcategory': dict(const.CATEGORY_TO_SUBCATEGORY)
    }
    return render(request, 'expenses/single_expense.html', context)


@login_required
@require_POST
def delete_expense(request, expense_id):
    try:
        expense = Expense.objects.get(pk=expense_id)
    except Expense.DoesNotExist:
        messages.warning(request, 'Expense does not exist.')
        return redirect(reverse('expenses:index'))
    expense.delete()
    messages.success(request, 'Expense successfully deleted!')
    return redirect(reverse('expenses:index'))


@login_required
@require_POST
def update_chart_months(request):
    """Update last n months displayed in chart"""
    request.session['show_last_x_months'] = int(request.POST['show_last_x_months'])
    messages.success(request, 'Chart successfully updated!')
    return redirect(reverse('expenses:index'))


# Todo
def clear(request):
    """Clear session"""
    request.session.clear()
    messages.success(request, 'Session cleared!')
    return redirect(reverse('expenses:index'))
