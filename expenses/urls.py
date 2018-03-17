from django.urls import path
from . import views


app_name = 'expenses'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    path('add/', views.add_expense, name='add_expense'),
    # path('add/', views.AddExpenseView.as_view(), name='add_expense'),
    path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    # path('edit/<int:pk>/', views.ExpenseUpdate.as_view(), name='edit_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('update_chart_months/', views.update_chart_months, name='update_chart_months'),
    path('register/', views.register, name='register'),
]
