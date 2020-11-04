from django.shortcuts import render, redirect
from apps.login_registration_app.models import User
from .models import *
from django.contrib import messages
from datetime import datetime, timedelta, date
from dateutil.parser import parse
from dateutil.relativedelta import *
import calendar
from PIL import Image

def home (request):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        user = User.objects.get(id=request.session['user_id'])
        # Get today's date
        today = date.today()

        # Create lists of expenses: all non-paid, and 14 days in future
        all_expenses = []
        for item in Expense.objects.all():
            if item.paid==False and len(item.name)>0:
                if item.due_date>(today-timedelta(days=7)) and item.due_date<(today+timedelta(days=14)):
                    all_expenses.append(item)
            
        # Create lists of incomes: all non-paid, and 14 days in future
        all_incomes = []
        for item in Income.objects.all():
            if item.earned==False and len(item.name)>0:
                if item.earn_date>(today-timedelta(days=7)) and item.earn_date<(today+timedelta(days=14)):
                    all_incomes.append(item)
        
        context = {
            "user":user,
            "all_expenses":all_expenses,
            "all_incomes":all_incomes
        }
        return render (request,'money_app/home.html', context)
    
def add(request):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        context = {
            "user": User.objects.get(id=request.session['user_id'])
        }
        return render (request, 'money_app/add.html', context)

def add_item(request):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            errors = Expense.objects.basicValidator(request.POST)
            if len(errors)>0:
                for key, value in errors.items():
                    messages.error(request, value)
                return redirect ('/m_m/home/add') 
            else:
                user = User.objects.get(id=request.session['user_id'])

                # Set end dates for one-time and ongoing items
                today = date.today()
                if len(request.POST['frequency'])<1: # one-time end-date is start-date
                    end_date = request.POST['due_date']
                elif len(request.POST['end_date'])<1: # ongoing lasts 10 years
                    end_date = today + timedelta(days=3650)
                else:
                    end_date = request.POST['end_date']
                    
                frequency=int(request.POST['frequency'])
                amount=round(float(request.POST['amount']), 2)
                
                # adding next recurrence of item
                def time_adder(due_date, frequency):
                    if frequency==1:
                        new_year = due_date.year
                        new_month = due_date.month + 1
                        if new_month > 12:
                            new_year += 1
                            new_month -= 12
                        last_day_of_month = calendar.monthrange(new_year, new_month)[1]
                        new_day = min(due_date.day, last_day_of_month)
                        due_date = due_date.replace(year=new_year, month=new_month, day=new_day)
                        due_date = due_date
                        return due_date
                    elif frequency>1:
                        due_date = due_date+timedelta(frequency)
                        return due_date
                    
                if (request.POST['category'] == "expense"):
                    messages.error(request, "Adding first occurence...")
                    new_expense = Expense.objects.create(user=user, name=request.POST['name'], amount=amount, frequency=frequency, due_date=request.POST['due_date'], end_date=end_date, paid=False)
                                       
                    # Get number of occurances from due-date to end-date
                    due_date=new_expense.due_date
                    time_difference = parse(new_expense.end_date)-parse(due_date)
                    num_of_occurances = int(time_difference/timedelta(new_expense.frequency))
                    
                    # Create all occurances until end date as long as frequency greater than 0
                    loops=0
                    messages.error(request, "Adding future occurances...")
                    while (loops<=num_of_occurances and frequency>0):
                        single_item = Expense.objects.filter(name=new_expense.name).order_by("created_at").last() # finds last item created to create the next one from that point
                        
                        # Run dateadder() to get future due date
                        due_date = time_adder(single_item.due_date, single_item.frequency)
                        
                        # Add future due date to future item
                        new_expense = Expense.objects.create(user=user, name=request.POST['name'], amount=amount, frequency=frequency, due_date=due_date, end_date=end_date, paid=False)
                        loops+=1
                    messages.error(request, "New expense added!")

                elif (request.POST['category'] == "income"):
                    messages.error(request, "Adding first occurence...")
                    new_income = Income.objects.create(user=user, name=request.POST['name'], amount=request.POST['amount'], frequency=frequency, earn_date=request.POST['due_date'], end_date=end_date, earned=False)
                                        
                    # Get number of occurances from due-date to end-date
                    due_date=request.POST['due_date']
                    num_of_occurances = parse(new_income.end_date)-parse(due_date)
                    num_of_occurances = int(num_of_occurances/timedelta(new_income.frequency))
                    
                    # Create all occurances until end date as long as frequency greater than 0
                    loops=0
                    messages.error(request, "Adding future occurances...")
                    while (loops<=num_of_occurances and frequency>0):
                        single_item = Income.objects.filter(name=new_income.name).order_by("created_at").last() # finds last item created to create the next one from that point
                        
                        # Run dateadder to get future due date
                        due_date = time_adder(single_item.earn_date, single_item.frequency)
                        
                        # Add future due date to future item
                        new_income = Income.objects.create(user=user, name=request.POST['name'], amount=request.POST['amount'], frequency=frequency, earn_date=due_date, end_date=end_date, earned=False)
                        loops+=1                    
                    messages.error(request, "New income added!")
                    
                elif (request.POST['category'] == "savings"):
                    messages.error(request, "Adding first occurence...")
                    new_savings = Income.objects.create(user=user, name=request.POST['name'], amount=request.POST['amount'], frequency=frequency, deposit_date=request.POST['due_date'], end_date=end_date, deposited=False)
                                        
                    # Get number of occurances from due-date to end-date
                    due_date=request.POST['due_date']
                    num_of_occurances = parse(new_expense.end_date)-parse(due_date)
                    num_of_occurances = int(num_of_occurances/timedelta(new_savings.frequency))
                    
                    # Create all occurances until end date as long as frequency greater than 0
                    loops=0
                    messages.error(request, "Adding future occurances...")
                    while (loops<=num_of_occurances and frequency>0):
                        single_item = Savings.objects.filter(name=new_savings.name).order_by("created_at").last() # finds last item created to create the next one from that point
                        
                        # Run dateadder() to get future due date
                        due_date = time_adder(single_item.deposit_date, single_item.frequency)
                        
                        # Add future due date to future item
                        new_savings = Savings.objects.create(user=user, name=request.POST['name'], amount=request.POST['amount'], frequency=frequency, deposit_date=due_date, end_date=end_date, deposited=False)
                        loops+=1                      
                        messages.error(request, "New savings added!")  
        return redirect ('/m_m/home/add')
    
def pay_expense(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            paid_expense = Expense.objects.get(id=id)
            paid_expense.paid=True
            paid_expense.save()
            messages.error(request, f"Awesome, {paid_expense.name} was logged as paid!")
        return redirect ('/m_m/home')

def log_income(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            earned_income = Income.objects.get(id=id)
            earned_income.earned=True
            earned_income.save()
            messages.error(request, f"Awesome, {earned_income.name} was logged as earned!")
        return redirect ('/m_m/home')

def edit_select(request):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.session['category']=='expense':
            display_item = Expense.objects.get(id=request.POST['item'])
        elif request.session['category']=='income':
            display_item = Income.objects.get(id=request.POST['item'])
        else:
            display_item = Savings.objects.get(id=request.POST['item'])
        return redirect (f'/m_m/home/edit_item/{display_item.id}')

def edit(request):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:   
        # Check to see if selected item was given from Edit page
        if 'selected_item' in request.session:
            selected_item = request.session.selected_item
        else:
            selected_item = {}
        
        if request.session['category']=='savings':
            all_items = Savings.objects.all()
        elif request.session['category']=='income':
            all_items = Income.objects.all()
        else:
            all_items = Expense.objects.all()
            
        context = {
            'user':User.objects.get(id=request.session['user_id']),
            'all_expenses':Expense.objects.all(),
            'all_income':Income.objects.all(),
            'all_savings':Savings.objects.all(),
            'all_items':all_items,
            'display_item':selected_item,
            'category':request.session['category']
        }
        return render(request, 'money_app/edit.html', context)
    
def select_category(request):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.POST['category']=='expense':
            request.session['category']="expense"
            return redirect ('/m_m/home/edit')
        elif request.POST['category']=='income':
            request.session['category']="income"
            return redirect ('/m_m/home/edit')
        else:
            request.session['category']=="savings"
        return redirect ('/m_m/home/edit')
        
def edit_expense(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        request.session['category']='expense'
        return redirect (f'/m_m/home/edit_item/{id}')
  
        
def edit_income(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        request.session['category']='income'
        return redirect (f'/m_m/home/edit_item/{id}')
      
        
def edit_item(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.session['category']=='expense':
            display_item = Expense.objects.get(id=id)
            context = {
                'user':User.objects.get(id=request.session['user_id']),
                'all_expenses':Expense.objects.all(),
                'all_income':Income.objects.all(),
                'all_savings':Savings.objects.all(),
                'category':request.session['category'],
                'display_item':display_item,
                'item_history':Expense.objects.filter(name=display_item.name, paid=True)
                }
            return render(request, 'money_app/edit.html', context) 
               
        elif request.session['category']=='income':
            display_item = Income.objects.get(id=id)
            context = {
                'user':User.objects.get(id=request.session['user_id']),
                'all_expenses':Expense.objects.all(),
                'all_income':Income.objects.all(),
                'all_savings':Savings.objects.all(),
                'category':request.session['category'],
                'display_item':display_item,
                'item_history':Income.objects.filter(name=display_item.name, earned=True)
                }
            return render(request, 'money_app/edit.html', context) 
        else:
            display_item = Savings.objects.get(id=id)
            context = {
                'user':User.objects.get(id=request.session['user_id']),
                'all_expenses':Expense.objects.all(),
                'all_income':Income.objects.all(),
                'all_savings':Savings.objects.all(),
                'category':request.session['category'],
                'display_item':display_item
                }
            return render(request, 'money_app/edit.html', context) 
        
def delete (request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            if request.session['category']=='expense':
                delete_item = Expense.objects.get(id=id)
            elif request.session['category']=='income':
                delete_item = Income.objects.get(id=id)
            else:
                request.session['category']=='savings'
                delete_item = Savings.objects.get(id=id)
            delete_item.delete()
            messages.error(request, "Item deleted")
        return redirect ('/m_m/home')