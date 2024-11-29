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

    # Read (GET)
    path('customers/<str:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/', views.customers_list, name='customers_list'),

    path('products/<str:product_id>/', views.product_detail, name='product_detail'),
    path('products/', views.products_list, name='products_list'),
    
    path('feedbacks/<str:feedback_id>/', views.feedback_detail, name='feedback_detail'),
    path('feedbacks/', views.feedbacks_list, name='feedbacks_list'),

    # Update (PATCH)
    path('customers/<str:customer_id>/update/', views.customer_update, name='customer_update'),
    path('customers/bulk_update/', views.bulk_update_customers, name='bulk_update_customers'),

    path('products/<str:product_id>/update/', views.product_update, name='product_update'),
    path('products/bulk_update/', views.bulk_update_products, name='bulk_update_products'),

    path('feedbacks/<str:feedback_id>/update/', views.feedback_update, name='feedback_update'),
    path('feedbacks/bulk_update/', views.bulk_update_feedbacks, name='bulk_update_feedbacks'),

    # Delete (DELETE)
    path('customers/<str:customer_id>/delete/', views.customer_delete, name='customer_delete'),
    path('customers/bulk_delete/', views.bulk_delete_customers, name='bulk_delete_customers'),

    path('products/<str:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/bulk_delete/', views.bulk_delete_products, name='bulk_delete_products'),
    
    path('feedbacks/<str:feedback_id>/delete/', views.feedback_delete, name='feedback_delete'),
    path('feedbacks/bulk_delete/', views.bulk_delete_feedbacks, name='bulk_delete_feedbacks'),


    # New URLs for added functionalities
    path('aggregation/customers/', views.customer_aggregation, name='customer_aggregation'),    # Aggregation query
    path('bulk-update/waist/', views.bulk_update_waist, name='bulk_update_waist'),              # Bulk update
    path('search/products/', views.product_keyword_search, name='product_keyword_search'),      # Complex filtering
]

