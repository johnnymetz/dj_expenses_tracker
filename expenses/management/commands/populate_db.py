from django.core.management.base import BaseCommand, CommandError
from expenses.models import Expense
from django.contrib.auth.models import User
from django.conf import settings
import expenses.constants as const

import pandas as pd
import xlrd
import datetime


class Command(BaseCommand):
    help = 'Populate the expense table with some data.'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', dest='delete', help='Delete all items in db')
        parser.add_argument('-f', '--file', dest='file', help='Excel file')

    def _parse_excel_sheet(self, path_to_file, sheetname):
        """Excel --> DF"""

        try:
            df = pd.read_excel(path_to_file, sheet_name=sheetname)
        except xlrd.biffh.XLRDError:
            return False, df, 'No sheet named <{}>'.format(sheetname)
        df.dropna(how='any', inplace=True)  # drop blank rows

        # validate
        if df.isnull().values.any():
            return False, df, 'Missing values'
        categories = [k for k in const.CATEGORY_TO_SUBCATEGORY.keys()]
        subcategories = []
        for v in const.CATEGORY_TO_SUBCATEGORY.values():
            subcategories += v
        if False in df['category'].isin(categories).unique():
            return False, df, 'Invalid category'
        elif False in df['subcategory'].isin(subcategories).unique():
            return False, df, 'Invalid subcategory'

        return True, df, None

    def _get_users(self):
        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)
        return [user1, user2]

    def _populate_expense_table(self, df, users):
        """DF --> DB"""
        for i, row in df.iterrows():
            for user in users:
                expense = Expense(
                    user=user,
                    item=row['item'],
                    cost=row['cost'],
                    date_purchased=row['date_purchased'],
                    category=row['category'],
                    subcategory=row['subcategory']
                )
                expense.save()

    def _create_dummy_expenses(self, user1, user2):
        now = datetime.datetime.now()
        few_days_ago = now - datetime.timedelta(days=5)
        last_month = now - datetime.timedelta(days=35)
        expense1 = Expense(user=user1, item='Urban Plates', cost=13.34, date_purchased=now,
                           category='Food', subcategory='Eat Out')
        expense1.save()
        expense2 = Expense(user=user1, item='Gas', cost=45, date_purchased=few_days_ago,
                           category='Car', subcategory='Gas')
        expense2.save()
        expense3 = Expense(user=user1, item='Amazon', cost=64.4, date_purchased=last_month,
                           category='Entertainment', subcategory='One-Timer')
        expense3.save()
        expense4 = Expense(user=user2, item='Vons', cost=25, date_purchased=now,
                           category='Food', subcategory='Grocery')
        expense4.save()
        expense5 = Expense(user=user2, item='Beer', cost=14, date_purchased=few_days_ago,
                           category='Entertainment', subcategory='Party')
        expense5.save()

    def handle(self, *args, **options):
        if options['file']:
            Expense.objects.all().delete()
            is_valid, df, error_message = self._parse_excel_sheet(
                options['file'],
                '2017'
            )
            if not is_valid:
                self.stdout.write(self.style.ERROR(error_message))
            else:
                users = self._get_users()
                self._populate_expense_table(df, users)
                self.stdout.write(self.style.SUCCESS('Expense items from excel added for {}'.format(users)))
        elif options['delete']:
            Expense.objects.all().delete()
            self.stdout.write(self.style.MIGRATE_HEADING('Successfully deleted all items from Expense table.'))
        else:
            user1, user2 = self._get_users()
            self._create_dummy_expenses(user1, user2)
            self.stdout.write(self.style.SUCCESS('Successfully added dummy items to Expense table.'))

