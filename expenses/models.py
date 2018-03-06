from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    food_limit = models.IntegerField(default=450, validators=[MinValueValidator(0)])
    car_limit = models.IntegerField(default=200, validators=[MinValueValidator(0)])
    entertainment_limit = models.IntegerField(default=550, validators=[MinValueValidator(0)])

    def monthly_limit(self):
        return sum([self.food_limit, self.car_limit, self.entertainment_limit])

    def __str__(self):
        return self.user.username


# Profile will be automatically created/updated when we create/update User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    item = models.CharField(max_length=100)
    cost = models.FloatField(validators=[MinValueValidator(0)])
    date_purchased = models.DateField(default=timezone.now)
    CATEGORY_CHOICES = ((k, k) for k in ['Food', 'Car', 'Entertainment'])
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    SUBCATEGORY_CHOICES = ((k, k) for k in ['Eat Out', 'Grocery', 'Gas', 'Car Maintenance',
                                            'Party', 'One-Timer', 'Gift'])
    subcategory = models.CharField(max_length=100, choices=SUBCATEGORY_CHOICES)

    def get_absolute_url(self):
        from django.urls import reverse
        # return reverse('expenses:edit_expense', kwargs={'pk': self.pk})
        return reverse('expenses:edit_expense', args=(self.pk,))

    def __str__(self):
        return '{} for ${:,.2f} for {}'.format(self.item, self.cost, self.user.username)
