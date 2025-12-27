from django.db import models

# Create your models here.
class Item(models.Model):
    name: str = models.CharField(max_length=255)
    description: str = models.CharField(max_length=500)
    price: float = models.FloatField(default=0)
    
    def __str__(self):
        return f"Name: {self.name}; Price: {self.price}"
    
class Discount(models.Model):
    name: str = models.CharField(max_length=50, default="Discount")
    percent_off: int = models.IntegerField(default=0) 
    
    def __str__(self):
        return f"{self.name} ({self.percent_off}%)"


class Tax(models.Model):
    name: str = models.CharField(max_length=50, default="Tax")
    rate: float = models.FloatField(default=0)
    
    def __str__(self):
        return f"{self.name} ({self.rate})"


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name='orders')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk}"

    def total_sum(self):
        total = sum(item.price for item in self.items.all())
        if self.discount:
            total = total * (1 - self.discount.percent_off / 100)
        if self.tax:
            total = total + (total * self.tax.rate/100)
            
        return round(total, 2)