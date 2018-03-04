from django.core.management.base import BaseCommand, CommandError
from expenses.models import Expense
import datetime


class Command(BaseCommand):
    help = 'Populate the expense table with some data.'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', dest='delete',
                            help='Delete all items in db')

    def _create_expenses(self):
        now = datetime.datetime.now()
        few_days_ago = now - datetime.timedelta(days=5)
        last_month = now - datetime.timedelta(days=35)
        expense1 = Expense(item='Urban Plates', cost=13.34, date_purchased=now,
                           category='Food', subcategory='Eat Out')
        expense1.save()
        expense2 = Expense(item='Gas', cost=45, date_purchased=few_days_ago,
                           category='Car', subcategory='Gas')
        expense2.save()
        expense3 = Expense(item='Amazon', cost=64.4, date_purchased=last_month,
                           category = 'Entertainment', subcategory = 'One-Timer')
        expense3.save()

    def handle(self, *args, **options):
        if options['delete']:
            Expense.objects.all().delete()
            self.stdout.write(self.style.MIGRATE_HEADING('Successfully deleted all items from Expense table.'))
        else:
            self._create_expenses()
            self.stdout.write(self.style.SUCCESS('Successfully added items to Expense table.'))
