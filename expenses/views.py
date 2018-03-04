from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import Expense
from .forms import ExpenseForm
from .helpers import sqlalchemy_objects_to_dicts, build_results
from . import constants as const
from .decorators import expense_required


@require_GET
@expense_required
def index(request):
    query_list = Expense.objects.all()
    assert query_list
    user_expenses = sqlalchemy_objects_to_dicts(query_list)
    results = build_results(user_expenses, request.session)

    context = {
        'user_expenses': user_expenses,
        'results': results,
        'category_to_subcategory': const.CATEGORY_TO_SUBCATEGORY
    }
    return render(request, 'expenses/index.html', context)


@require_http_methods(["GET", "POST"])
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense successfully added!')
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
            form.save()
            messages.success(request, 'Expense successfully updated!')
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
