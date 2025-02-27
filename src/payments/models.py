from django.core.validators import MinValueValidator
from django.db import models


class Item(models.Model):
    CURRENCY_CHOICES = [
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField(validators=[MinValueValidator(1)])
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd')

    def __str__(self):
        return f"{self.name} ({self.price} {self.currency.upper()})"


class Discount(models.Model):
    name = models.CharField(max_length=100)
    percent_off = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    stripe_coupon_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.percent_off}% off)"


class Tax(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    stripe_tax_rate_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    items = models.ManyToManyField(Item)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_amount(self):
        total = sum(item.price for item in self.items.all())
        if self.discount:
            total = total * (1 - self.discount.percent_off / 100)
        if self.tax:
            total = total * (1 + self.tax.rate / 100)
        return int(total)

    def __str__(self):
        return f"Order #{self.id} ({self.status})"
