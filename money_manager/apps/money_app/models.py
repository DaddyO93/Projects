from django.db import models
from apps.login_registration_app.models import User

class Manager (models.Manager):
    def basicValidator (self, postData):
        errors = {}
        if len(postData['category'])<1:
            errors['category'] = "Please select a category for this item"
        if len(postData['frequency'])<1:
            errors['frequency'] = "Please select the frequency for this item"
        if len(postData['name'])<2:
            errors['name'] = "Please use a name longer than 2 characters"
        if float(postData['amount'])<0:
            errors['amount'] = "Please enter an amount greater than $0"
        return errors

class Expense(models.Model):
    user = models.ForeignKey(User, related_name="user_expense", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    amount = models.FloatField()
    due_date = models.DateField()
    end_date = models.DateField()
    frequency = models.IntegerField()
    # recurrence = RecurrenceField()
    paid = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = Manager()
    
class Receipts(models.Model):
    note = models.TextField()
    receipt_image = models.ImageField()
    receipt_for = models.ForeignKey(Expense, related_name="receipts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Income(models.Model):
    user = models.ForeignKey(User, related_name="user_income", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    amount = models.FloatField()
    earn_date = models.DateField()
    end_date = models.DateField()
    frequency = models.IntegerField()
    # recurrence = RecurrenceField()
    earned = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = Manager()
    
class PayStub(models.Model):
    note = models.TextField()
    paystub_image = models.ImageField()
    paystub_for = models.ForeignKey(Income, related_name="paystub", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
              
class Savings(models.Model):
    user = models.ForeignKey(User, related_name="user_savings", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    amount = models.FloatField()
    deposit_date = models.DateField()
    end_date = models.DateField()
    frequency = models.IntegerField()
    # recurrence = RecurrenceField()
    deposited = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = Manager()
