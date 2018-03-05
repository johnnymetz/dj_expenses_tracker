from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Expense, Profile


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('item', 'get_cost', 'date_purchased', 'category', 'subcategory', 'user')
    list_filter = ['item', 'cost', 'date_purchased', 'category', 'subcategory', 'user']
    search_fields = ['item', 'get_cost', 'date_purchased', 'category', 'subcategory', 'user']

    def get_cost(self, instance):
        return '${:,.2f}'.format(instance.cost)
    get_cost.short_description = 'Cost / Price'


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_monthly_limit')
    list_select_related = ('profile',)

    def get_monthly_limit(self, instance):
        return '${:,.0f}'.format(instance.profile.monthly_limit())
    get_monthly_limit.short_description = 'Monthly Limit'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(Expense, ExpenseAdmin)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
