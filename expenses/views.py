from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST, require_http_methods

from .models import Expense
from .forms import ExpenseForm, ProfileForm
from .helpers import sqlalchemy_objects_to_dicts, build_results
from . import constants as const

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView, UpdateView
from django.utils.decorators import method_decorator


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
            return redirect('expenses:index')
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)


@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    messages.success(request, "You've been successfully logged out")


# INDEX
# @login_required
# @require_http_methods(['GET', 'POST'])
# def index(request):
#     query_list = request.user.expenses.all()
#     if not query_list:
#         messages.info(request, 'Please add an expense to get started!')
#         return redirect('expenses:add_expense')
#
#     assert query_list
#     user_expenses = sqlalchemy_objects_to_dicts(query_list)
#     results = build_results(user_expenses, request.session)
#
#     if request.method == 'POST':
#         profile_form = ProfileForm(request.POST, instance=request.user.profile)
#         if profile_form.is_valid():
#             # database validators satisfied
#             profile_form.save()
#             messages.success(request, 'Monthly limits successfully updated!')
#         else:
#             messages.error(request, 'Something went wrong...')
#     else:
#         profile_form = ProfileForm(instance=request.user.profile)
#
#     context = {
#         'profile_form': profile_form,
#         'user_expenses': user_expenses,
#         'results': results,
#         'category_to_subcategory': const.CATEGORY_TO_SUBCATEGORY
#     }
#     return render(request, 'expenses/index.html', context)


@method_decorator(login_required, name='dispatch')
class IndexView(View):
    form_class = ProfileForm
    template_name = 'expenses/index.html'
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        query_list = request.user.expenses.all()
        if not query_list:
            messages.info(request, 'Please add an expense to get started!')
            return redirect(self.request.path)
        assert query_list
        user_expenses = sqlalchemy_objects_to_dicts(query_list)
        results = build_results(user_expenses, request.session)
        profile_form = self.form_class(instance=request.user.profile)
        context = {
            'profile_form': profile_form,
            'user_expenses': user_expenses,
            'results': results,
            'category_to_subcategory': const.CATEGORY_TO_SUBCATEGORY
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        query_list = request.user.expenses.all()
        if not query_list:
            messages.info(request, 'Please add an expense to get started!')
            return redirect('expenses:add_expense')
        assert query_list
        user_expenses = sqlalchemy_objects_to_dicts(query_list)
        results = build_results(user_expenses, request.session)
        profile_form = self.form_class(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Monthly limits successfully updated!')
        else:
            messages.error(request, 'Something went wrong...')
        context = {
            'profile_form': profile_form,
            'user_expenses': user_expenses,
            'results': results,
            'category_to_subcategory': const.CATEGORY_TO_SUBCATEGORY
        }
        return render(request, self.template_name, context)


# ADD EXPENSE
# 1. regular view
# 2. class-based: get, post
# 3. class_based: FormView (uses forms.py)
# 4. class_based: CreateView (skips forms.py)
@login_required
@require_http_methods(['GET', 'POST'])
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

    context = {
        'expense_action': 'add',
        'form': form,
        'categories': list(const.CATEGORY_TO_SUBCATEGORY.keys()),
        'category_to_subcategory': dict(const.CATEGORY_TO_SUBCATEGORY)
    }
    return render(request, 'expenses/single_expense.html', context)


# @method_decorator([login_required], name='dispatch')
# class AddExpenseView(FormView):
#     """Pretty much the same. Only difference is that it empties form on POST."""
#     form_class = ExpenseForm
#     template_name = 'expenses/single_expense.html'
#     success_url = reverse_lazy('expenses:add_expense')
#     http_method_names = ['get', 'post']
#
#     def form_valid(self, form):
#         # Called when form data is POSTed
#         expense = form.save(commit=False)
#         expense.user = self.request.user
#         expense.save()
#         messages.success(self.request, 'Expense successfully added!')
#         return super().form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['expense_action'] = 'add'
#         context['categories'] = list(const.CATEGORY_TO_SUBCATEGORY.keys())
#         context['category_to_subcategory'] = dict(const.CATEGORY_TO_SUBCATEGORY)
#         return context


# EDIT EXPENSE
@login_required
@require_http_methods(['GET', 'POST'])
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    if expense.user != request.user:
        raise PermissionDenied

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

    context = {
        'expense_action': 'edit',
        'expense': expense,
        'form': form,
        'categories': list(const.CATEGORY_TO_SUBCATEGORY.keys()),
        'category_to_subcategory': dict(const.CATEGORY_TO_SUBCATEGORY)
    }
    return render(request, 'expenses/single_expense.html', context)


# @method_decorator([login_required], name='dispatch')
# class ExpenseUpdate(UpdateView):
#     """Skips forms.py: don't get placeholders, date format, etc."""
#     model = Expense
#     fields = ['item', 'cost', 'date_purchased', 'category', 'subcategory']
#     template_name = 'expenses/single_expense.html'
#     http_method_names = ['get', 'post']
#
#     def form_valid(self, form):
#         # Called when form data is POSTed
#         expense = form.save(commit=False)
#         expense.user = self.request.user
#         expense.save()
#         messages.success(self.request, 'Expense successfully updated!')
#         return super().form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['expense_action'] = 'edit'
#         # context['expense'] = self.get_object()  # already passed by default
#         context['categories'] = list(const.CATEGORY_TO_SUBCATEGORY.keys())
#         context['category_to_subcategory'] = dict(const.CATEGORY_TO_SUBCATEGORY)
#         return context
#
#     def get_success_url(self):
#         # default = 'same_url/None'
#         # print(self.request.build_absolute_uri())
#         return self.request.path


@login_required
@require_POST
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    if expense.user != request.user:
        raise PermissionDenied
    else:
        expense.delete()
        messages.success(request, 'Expense successfully deleted!')
        return redirect('expenses:index')


@login_required
@require_POST
def update_chart_months(request):
    """Update last n months displayed in chart"""
    request.session['show_last_x_months'] = int(request.POST['show_last_x_months'])
    messages.success(request, 'Chart successfully updated!')
    # return redirect(reverse('expenses:index'))  # reverse url name
    return redirect('expenses:index')  # url name
    # expense = Expense.objects.all()[0]
    # return redirect(expense)  # expense.get_absolute_url
    # return redirect('expenses:edit_expense', expense_id=expense.id)


# Todo
def clear(request):
    """Clear session"""
    request.session.clear()
    messages.success(request, 'Session cleared!')
    return redirect('expenses:index')
