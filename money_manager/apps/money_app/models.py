from django.db import models
from apps.login_registration_app.models import User

class Manager (models.Manager):
    def basicValidator (self, postData):
        errors = {}
        if len(postData['name'])<2:
            errors['name'] = "Please use a name longer than 2 characters"
        if float(postData['amount'])<0:
            errors['amount'] = "Please enter an amount greater than $0"
        name = postData['name']
        if name in Item.objects.all():
            errors['name'] = "That name is already taken"
        return errors

class Item(models.Model):
    user = models.ForeignKey(User, related_name="user_expense", on_delete=models.CASCADE)
    category = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    amount = models.FloatField()
    due_date = models.DateField()
    end_date = models.DateField()
    frequency = models.IntegerField()
    logged = models.BooleanField()
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = Manager()
    
class Receipts(models.Model):
    receipt_image = models.ImageField()
    receipt_for = models.ForeignKey(Item, related_name="receipts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class PayStub(models.Model):
    paystub_image = models.ImageField()
    paystub_for = models.ForeignKey(Item, related_name="paystub", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
