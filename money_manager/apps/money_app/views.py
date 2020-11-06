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
        request.session['category']=""
        # Get today's date
        today = date.today()

        # Create lists of items: all non-paid, and due 7 days past and 14 days in future
        all_items = []
        for item in Item.objects.all():
            if item.logged==False and len(item.name)>0:
                if item.due_date<(today+timedelta(days=14)):
                    all_items.append(item)
        
        # get total deposits, expenses, and incomes
        total_expenses = 0
        total_income = 0
        total_deposited = 0
        paid_expenses = Item.objects.filter(category='expense', logged=True)
        earned_income = Item.objects.filter(category='income', logged=True)
        deposited_items = Item.objects.filter(category='savings', logged=True)
        
        for object in paid_expenses:
            total_expenses += object.amount
        for object in earned_income:
            total_income += object.amount
        for object in deposited_items:
            total_deposited += object.amount
        total_difference = (total_income-total_expenses) + total_deposited 
                      
        due_this_month = []  
        everything = Item.objects.all()
        for item in everything:
            if item.due_date.month == today.month:
                due_this_month.append(item)
        
        expense_this_month=0
        income_this_month=0
        savings_this_month=0
        for item in due_this_month:
            if item.category == 'expense':
                expense_this_month += item.amount
            elif item.category == 'income':
                income_this_month += item.amount
            elif item.category == 'savings':
                savings_this_month += item.amount

        remainder = income_this_month-(expense_this_month+savings_this_month)
              
        context = {
            "user":user,
            "total_expenses":total_expenses,
            "total_income":total_income,
            "total_deposited":total_deposited,
            "all_items":all_items,
            "total_difference":total_difference, 
            'expense_this_month':expense_this_month,         
            'income_this_month':income_this_month,         
            'savings_this_month':savings_this_month,   
            'remainder':remainder,      
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
        print("validator issue")
        if request.method =='POST':
            errors = Item.objects.basicValidator(request.POST)
            if len(errors)>0:
                for key, value in errors.items():
                    messages.error(request, value)
                return redirect ('/m_m/home/add') 
            else:
                user = User.objects.get(id=request.session['user_id'])
                due_date = request.POST['due_date']
                end_date = request.POST['end_date']
                frequency=int(request.POST['frequency'])
                amount=round(float(request.POST['amount']), 2)

                # Set end dates for one-time and ongoing items
                today = date.today()
                if frequency==0: # one-time end-date is start-date
                    end_date = due_date
                elif len(end_date)<1: # ongoing lasts 5 years
                    end_date = today + timedelta(days=1825)
                else:
                    end_date = end_date
                
                messages.error(request, f"Adding first occurence of {request.POST['name']}")
                new_item = Item.objects.create(user=user, category=request.POST['category'], name=request.POST['name'], amount=amount, due_date=due_date, end_date=end_date, frequency=frequency, logged=False, note=request.POST['note'])
                
                # Create all occurances until end date as long as frequency greater than 0
                loops=0
                if frequency>0:
                    messages.error(request, f"Adding future occurances of {request.POST['name']}")
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
                    
                    # Get number of occurances from due-date to end-date
                    due_date=new_item.due_date
                    time_difference = parse(new_item.end_date)-parse(due_date)
                    num_of_occurances = int(time_difference/timedelta(new_item.frequency))
                    while (loops<=num_of_occurances and frequency>0):
                        single_item = Item.objects.filter(name=new_item.name).order_by("created_at").last() # finds last item created to create the next one from that point
                        
                        # Run dateadder() to get future due date
                        due_date = time_adder(single_item.due_date, single_item.frequency)
                        
                        # Add future due date to future item
                        new_item = Item.objects.create(user=user, category=request.POST['category'], name=request.POST['name'], amount=amount, due_date=due_date, end_date=end_date, frequency=frequency, logged=False, note=request.POST['note'])
                        loops+=1
                    messages.error(request, f"New {new_item.name} added!") 
            return redirect ('/m_m/home/add')
    
def log_item(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            logged_item = Item.objects.get(id=id)
            logged_item.logged=True
            logged_item.save()
            messages.error(request, f"Awesome, {logged_item.name} was entered!")
        return redirect ('/m_m/home')

def edit(request):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:   
        context = {
            'user':User.objects.get(id=request.session['user_id']),
            'all_items':Item.objects.all(),
            'category':request.session['category']
        }
        return render(request, 'money_app/edit.html', context)
    
def select_category(request, cat_id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if cat_id==1:
            request.session['category']="income"
        elif cat_id==2:
            request.session['category']="expense"
        elif cat_id==3:
            request.session['category']="savings"
        else:
            request.POST['category']=""
        return redirect ('/m_m/home/edit')
        
def edit_item(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        display_item = Item.objects.filter(id=id)[0]
        request.session['category']=display_item.category
        disable_buttons=False
        context = {
            'user':User.objects.get(id=request.session['user_id']),
            'all_items':Item.objects.all(),
            'category':request.session['category'],
            'display_item':display_item,
            'disable_buttons':disable_buttons,
            'item_history':Item.objects.filter(name=display_item.name, logged=True)
            }
        return render(request, 'money_app/edit.html', context) 
                       
def delete_single (request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            delete_item = Item.objects.get(id=id)
            delete_item.delete()
            messages.error(request, "Item deleted")
        return redirect ('/m_m/home')
    
def delete_all (request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            today = date.today()
            item_to_delete = Item.objects.get(id=id)
            
            # Find all items by same name, then delete all 
            list_of_ids=[]
            all_items_to_delete = Item.objects.filter(name=item_to_delete.name)
            loops=len(all_items_to_delete)
            for single_item in all_items_to_delete:
                list_of_ids.append(single_item.id)
                    
            for item_id in list_of_ids:
                item_to_delete = Item.objects.get(id=item_id)
                item_to_delete.delete()     
                       
            messages.error(request, "All occurences deleted")
        return redirect ('/m_m/home')
   
def delete_future (request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            today = date.today()
            item_to_delete = Item.objects.get(id=id)
            
            # Find all items by same name, then delete all 
            list_of_ids=[]
            all_items_to_delete = Item.objects.filter(name=item_to_delete.name)
            loops=len(all_items_to_delete)
            for single_item in all_items_to_delete:
                if single_item.due_date>today:
                    list_of_ids.append(single_item.id)
                    
            for item_id in list_of_ids:
                item_to_delete = Item.objects.get(id=item_id)
                item_to_delete.delete()     
                       
            messages.error(request, "Future occurences deleted")
        return redirect ('/m_m/home')
    
def update_future (request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            today = date.today()
            item_to_update = Item.objects.get(id=id)
            
            # delete all future occurances so are no duplicates
            future_items = Item.objects.filter(name=item_to_update.name)
            loops=len(future_items)
            list_of_ids=[]
            for single_item in future_items:
                if single_item.due_date>today:
                    list_of_ids.append(single_item.id)
                    
            for item_id in list_of_ids:
                item_to_delete = Item.objects.get(id=item_id)
                item_to_delete.delete()
            
            # Send to Add to create all future occurances
            request.session.method='POST'
        return redirect ('/m_m/home/add_item')
            
def update_single(request, id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect ('/')
    else:
        if request.method =='POST':
            item_to_update = Item.objects.get(id=id)
            item_to_update.name=request.POST['name']
            item_to_update.amount=request.POST['amount']
            return redirect ('/m_m/home/edit')