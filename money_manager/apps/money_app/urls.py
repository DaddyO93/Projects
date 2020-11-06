from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home),
    path('home/add', views.add),
    path('home/add_item', views.add_item),
    path('home/logged/<int:id>', views.log_item),
    path('home/edit', views.edit),
    path('home/select_category/<int:cat_id>', views.select_category),
    # path('home/edit_select/<int:id>', views.edit_select),
    path('home/edit_item/<int:id>', views.edit_item),
    path('home/delete_single/<int:id>', views.delete_single),
    path('home/delete_all/<int:id>', views.delete_all),
    path('home/delete_future/<int:id>', views.delete_future),
    path('home/update_future/<int:id>', views.update_future),
    path('home/update_single/<int:id>', views.update_single)
]