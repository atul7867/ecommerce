from django.db import models
from django import forms

# Create your models here.
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    msg = models.TextField()

    def __str__(self):
        return self.name
    



class Enrollment(models.Model):
    username = models.CharField(max_length=100)
    payment_date = models.DateField()
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    whatsapp_no = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username
    
class Payment(models.Model):
    razorpay_order_id = models.CharField(max_length=100)
    # Add other fields as needed, such as amount, timestamp, etc.
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment ID: {self.id}, Razorpay Order ID: {self.razorpay_order_id}"