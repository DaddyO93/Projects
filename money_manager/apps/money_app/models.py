from django.db import models
from apps.login_registration_app.models import User
from recurrence.fields import RecurrenceField


# Validator for the Expense category
class ExpenseManager (models.Manager):
    def expenseValidator (self, postData):
        errors = {}
        if len(postData['display_name'])<2:
            errors['display_name'] = "Please use a name longer than 2 characters"
        if postData['amount']<0:
            errors['amount'] = "Please enter an amount greater than $0"
        if len(postData['expense_type'])<2:
            errors['expense_type'] = "Please select an expense type (e.g. Groceries, Utilities, etc.)"
        return errors

class Expense(models.Model):
    user_expense = models.ForeignKey(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=4, decimal_places=2)
    expense_type = models.CharField(max_length=20)
    recurring = models.BooleanField()
    due_date = models.DateField()
    paid = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ExpenseManager.expenseValidator()
    
class Receipts(models.Model):
    date_paid = models.DateField()
    note = models.TextField()
    receipt_image = models.ImageField()
    receipt_for = models.ForeignKey(Expense, related_name="receipts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Validator for Income category
class IncomeSavingsManager(models.Manager):
    def incomeSavingsValidator(self, postData):
        errors = {}
        if len(postData['display_name'])<2:
            errors['display_name'] = "Please use a name longer than 2 characters"
        if postData['amount']<0:
            errors['amount'] = "Please enter an amount greater than $0"
        return errors

class Income(models.Model):
    user_income = models.ForeignKey(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=4, decimal_places=2)
    income_type = models.CharField(max_length=20)
    recurring = models.BooleanField()
    earn_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = IncomeSavingsManager.incomeSavingsValidator()
            
class Savings(models.Model):
    user_savings = models.ForeignKey(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=4, decimal_places=2)
    start = models.TimeField()
    end = models.TimeField()
    recurrences = RecurrenceField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = IncomeSavingsManager.incomeSavingsValidator()

# Category, Account, Income, Expense, and Savings
class AccountOrganizationManager(models.Manager):
    def nameValidator (self, postData):
        errors = {}
        if len(postData['name'])<2:
            errors['name'] = "Please use a name longer than 2 characters"
        return errors

class IncomeCategory(models.Model):
    name = models.CharField(max_length=50)
    income_category = models.ManyToManyField(Income, related_name='income_category')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AccountOrganizationManager.nameValidator()
    
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=50)
    expense_category = models.ManyToManyField(Income, related_name='expense_category')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AccountOrganizationManager.nameValidator()

class SavingsCategory(models.Model):
    name = models.CharField(max_length=50)
    savings_category = models.ManyToManyField(Income, related_name='savings_category')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AccountOrganizationManager.nameValidator()
    
class Account(models.Model):
    name = models.CharField(max_length=50)
    expense_for = models.ManyToManyField(Expense, related_name='expense_account')
    income_for = models.ManyToManyField(Income, related_name='income_account')
    savings_for = models.ManyToManyField(Savings, related_name='savings_account')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AccountOrganizationManager.nameValidator()
    
# Source/Destination organization/individual
class Organization(models.Model):
    name = models.CharField(max_length=50)
    income = models.ManyToManyField(Income, related_name='income_source')
    expense = models.ManyToManyField(Expense, related_name='expense_destination')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AccountOrganizationManager.nameValidator()
