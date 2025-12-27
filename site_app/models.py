from django.db import models

# Create your models here.
class Item(models.Model):
    name: str = models.CharField(max_length=255)
    description: str = models.CharField(max_length=500)
    price: float = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    
    def __str__(self):
        return f"Name: {self.name}; Price: {self.price}"
    
class Order(models.Model):
    items = models.ManyToManyField(Item, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def total_sum(self):
        total = sum(item.price for item in self.items.all())
        return round(total, 2)
    
    def __str__(self):
        return f"Order num: #{self.pk}"