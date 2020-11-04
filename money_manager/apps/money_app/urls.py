from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home),
    path('home/add', views.add),
    path('home/add_item', views.add_item),
    path('home/paid/<int:id>', views.pay_expense),
    path('home/earned/<int:id>', views.log_income),
    path('home/edit', views.edit),
    path('home/edit_expense/<int:id>', views.edit_expense),
    path('home/edit_income/<int:id>', views.edit_income),
    path('home/edit_item/<int:id>', views.edit_item),
    path('home/delete/<int:id>', views.delete),
    path('home/select_category', views.select_category),
    path('home/edit_select', views.edit_select),
]