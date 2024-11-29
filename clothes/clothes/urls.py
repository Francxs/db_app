"""
URL configuration for clothes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # db list
    path('customers/', views.customer_list, name='customer_list'),
    path('products/', views.product_list, name='product_list'),
    path('feedbacks/', views.feedback_list, name='feedback_list'),

    # New Entries POST method
    path('customer/create/', views.customer_create, name='customer_create'),
    path('product/create/', views.product_create, name='product_create'),
    path('feedback/create/', views.feedback_create, name='feedback_create'),

    # Bulk Uploads
    path('upload/customers/', views.bulk_upload_customers, name='bulk_upload_customers'),
    path('upload/products/', views.bulk_upload_products, name='bulk_upload_products'),
    path('upload/feedbacks/', views.bulk_upload_feedbacks, name='bulk_upload_feedbacks'),

    # Text File JSON Uploads
    path('upload/customers/txt/', views.upload_customers_from_txt, name='upload_customers_txt'),
    path('upload/products/txt/', views.upload_products_from_txt, name='upload_products_txt'),
    path('upload/feedbacks/txt/', views.upload_feedbacks_from_txt, name='upload_feedbacks_txt'),

    # New routes for customer and product feedbacks
    path('customer/<int:user_id>/feedbacks/', views.customer_feedbacks, name='customer_feedbacks'),
    path('product/<int:item_id>/feedbacks/', views.product_feedbacks, name='product_feedbacks'),

    # New URLs for added functionalities
    path('aggregation/customers/', views.customer_aggregation, name='customer_aggregation'),    # Aggregation query
    path('bulk-update/waist/', views.bulk_update_waist, name='bulk_update_waist'),              # Bulk update
    path('search/products/', views.product_keyword_search, name='product_keyword_search'),      # Complex filtering
]

