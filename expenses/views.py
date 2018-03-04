from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import Expense
from .helpers import sqlalchemy_objects_to_dicts, build_results
from . import constants as const
from .decorators import expense_required
import datetime


@require_GET
@expense_required
def index(request):
    print(request.session.items())
    query_list = Expense.objects.all()
    assert query_list
    user_expenses = sqlalchemy_objects_to_dicts(query_list)
    results = build_results(user_expenses, request.session)

    context = {
        'user_expenses': user_expenses,
        'results': results,
        # 'monthly_limit': monthly_limit,
        # 'user_months': user_months,
        # 'chart_data': chart_data,
        # 'data': chart_data['data'],
        # 'labels': chart_data['labels'],
        # 'limit_exceeded': chart_data['limit_exceeded'],
        'category_to_subcategory': const.CATEGORY_TO_SUBCATEGORY
    }
    return render(request, 'expenses/index.html', context)


@require_http_methods(["GET", "POST"])
def add_expense(request):
    if request.method == 'POST':
        expense = Expense(
            item=request.POST['item'],
            cost=float(request.POST['cost']),
            date_purchased=datetime.datetime.strptime(request.POST['date_purchased'], '%m/%d/%Y'),
            category=request.POST['category'],
            subcategory=request.POST['subcategory']
        )
        expense.save()
        messages.success(request, 'Expense successfully added!')

    pk_to_expense = {i.id: {'item': i.item,
                            'cost': i.cost,
                            'date_purchased': i.date_purchased,
                            'category': i.category,
                            'subcategory': i.subcategory} for i in Expense.objects.all()}
    context = {
        'expense_action': 'add',
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
        expense.item = request.POST['item']
        expense.cost = float(request.POST['cost'])
        expense.date_purchased = datetime.datetime.strptime(request.POST['date_purchased'], '%m/%d/%Y')
        expense.category = request.POST['category']
        expense.subcategory = request.POST['subcategory']
        expense.save()
        messages.success(request, 'Expense successfully updated!')

    pk_to_expense = {i.id: {'item': i.item,
                            'cost': i.cost,
                            'date_purchased': i.date_purchased,
                            'category': i.category,
                            'subcategory': i.subcategory} for i in Expense.objects.all()}
    context = {
        'expense_action': 'edit',
        'expense': expense,
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
