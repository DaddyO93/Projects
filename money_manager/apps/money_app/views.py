from django.shortcuts import render, redirect
from apps.login_registration_app.models import User
from .models import *
from django.contrib import messages
from datetime import date

# {{ form.media }} in HTML needed to use the date-picker for recurrence to work

# Create your views here.
def index (request):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        today = date.today()
        past_expenses = []
        upcoming_expenses = []
        past_due_expenses = []
        for expense in Expense.objects.all():
            if expense.due_date < today and expense.due_date > (today - 14):
                past_expenses.append(expense)
            elif expense.due_date >= today and expense.due_date < (today + 30):
                upcoming_expenses.append(expense)
            elif expense.due_date < (today - 14) and expense.paid == False:
                past_due_expenses.append(expense)

        context = {
            "user":User.objects.get(id=request.session['user_id']),
            "past_expenses":past_expenses.order_by('due_date'),
            "upcoming_expenses":upcoming_expenses.order_by('-due_date'),
            "past_due_expenses":past_due_expenses.order_by('-due_date'),
            "income_categories":IncomeCategory.objects.all(),
            "expense_categories":ExpenseCategory.objects.all(),
            "savings_categories":SavingsCategory.objects.all(),
        }
        return render (request,' index.html', context)
    
# When creating income/expense/savings, earn_date/due_date/transfer_date