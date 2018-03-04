from django.db import models


class Expense(models.Model):
    item = models.CharField(max_length=100)
    cost = models.FloatField()
    date_purchased = models.DateField()
    CATEGORY_CHOICES = ((k, k) for k in ['Food', 'Car', 'Entertainment'])
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    SUBCATEGORY_CHOICES = ((k, k) for k in ['Eat Out', 'Grocery', 'Gas', 'Car Maintenance',
                                            'Party', 'One-Timer', 'Gift'])
    subcategory = models.CharField(max_length=100, choices=SUBCATEGORY_CHOICES)

    def __str__(self):
        return '<{} for ${:,.2f}>'.format(self.item, self.cost)
