from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CustomerSerializer, ProductSerializer, FeedbackSerializer
from .models import Customer, Product, Feedback
from .utils import get_db_handle
from django.core.files.uploadedfile import UploadedFile
import json
from rest_framework.exceptions import ValidationError

# MongoEngine views for common operations
@api_view(['GET'])
def customer_list(request):
    customers = Customer.objects.all()  # MongoEngine query to get all customers
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()  # MongoEngine query to get all products
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def feedback_list(request):
    feedbacks = Feedback.objects.all()  # MongoEngine query to get all feedback
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)

# Create a new customer
@api_view(['POST'])
def customer_create(request):
    serializer = CustomerSerializer(data=request.data)  # Deserialize the data
    if serializer.is_valid():
        serializer.save()  # Save the new customer
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create a new product
@api_view(['POST'])
def product_create(request):
    serializer = ProductSerializer(data=request.data)  # Deserialize the data
    if serializer.is_valid():
        serializer.save()  # Save the new product
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def feedback_create(request):
    serializer = FeedbackSerializer(data=request.data)  # Deserialize the data
    if serializer.is_valid():
        try:
            serializer.save()  # Save the new feedback
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PyMongo Views for Bulk Uploads

# 1. Bulk Upload Customers (PyMongo)
@api_view(['POST'])
def bulk_upload_customers(request):
    """Bulk upload customers using PyMongo."""
    db_handle, _ = get_db_handle()  # Get the PyMongo database handle
    try:
        # Insert multiple customer documents at once
        result = db_handle['customers'].insert_many(request.data)
        return Response({"inserted_ids": [str(i) for i in result.inserted_ids]}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 2. Bulk Upload Products (PyMongo)
@api_view(['POST'])
def bulk_upload_products(request):
    """Bulk upload products using PyMongo."""
    db_handle, _ = get_db_handle()  # Get the PyMongo database handle
    try:
        # Insert multiple product documents at once
        result = db_handle['products'].insert_many(request.data)
        return Response({"inserted_ids": [str(i) for i in result.inserted_ids]}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 3. Bulk Upload Feedbacks (PyMongo)
@api_view(['POST'])
def bulk_upload_feedbacks(request):
    """Bulk upload feedback using PyMongo."""
    db_handle, _ = get_db_handle()  # Get the PyMongo database handle
    try:
        # Insert multiple feedback documents at once
        result = db_handle['feedback'].insert_many(request.data)
        return Response({"inserted_ids": [str(i) for i in result.inserted_ids]}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def upload_customers_from_txt(request):
    """Upload customers from a .txt file using PyMongo."""
    db_handle, _ = get_db_handle()  # Get the PyMongo database handle

    # Check if the file is provided
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']

    # Check if the uploaded file is valid
    if not isinstance(file, UploadedFile):
        return Response({"error": "Invalid file format"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Read and parse the .txt file content
        file_content = file.read().decode('utf-8')
        customer_data = [json.loads(line) for line in file_content.splitlines()]

        # Insert multiple customer documents at once
        result = db_handle['customers'].insert_many(customer_data)
        return Response({"inserted_ids": [str(i) for i in result.inserted_ids]}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def upload_feedbacks_from_txt(request):
    """Upload feedbacks from a .txt file using PyMongo."""
    db_handle, _ = get_db_handle()  # Get the PyMongo database handle

    # Check if the file is provided
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']

    # Check if the uploaded file is valid
    if not isinstance(file, UploadedFile):
        return Response({"error": "Invalid file format"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Read and parse the .txt file content
        file_content = file.read().decode('utf-8')
        customer_data = [json.loads(line) for line in file_content.splitlines()]

        # Insert multiple customer documents at once
        result = db_handle['customers'].insert_many(customer_data)
        return Response({"inserted_ids": [str(i) for i in result.inserted_ids]}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_products_from_txt(request):
    """Upload products from a .txt file using PyMongo."""
    db_handle, _ = get_db_handle()  # Get the PyMongo database handle

    # Check if the file is provided
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']

    # Check if the uploaded file is valid
    if not isinstance(file, UploadedFile):
        return Response({"error": "Invalid file format"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Read and parse the .txt file content
        file_content = file.read().decode('utf-8')
        customer_data = [json.loads(line) for line in file_content.splitlines()]

        # Insert multiple customer documents at once
        result = db_handle['customers'].insert_many(customer_data)
        return Response({"inserted_ids": [str(i) for i in result.inserted_ids]}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# Customer

@api_view(['GET'])
def customer_detail(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def customer_update(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Bulk Update

@api_view(['PATCH'])
def bulk_update_customers(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    update = request.data.get('update')
    try:
        result = db_handle['customers'].update_many(filter, {'$set': update})
        return Response({"matched_count": result.matched_count, "modified_count": result.modified_count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def customer_delete(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# Bulk Delete
@api_view(['DELETE'])
def bulk_delete_customers(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    try:
        result = db_handle['customers'].delete_many(filter)
        return Response({"deleted_count": result.deleted_count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Product

@api_view(['GET'])
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def product_update(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# Bulk Update
@api_view(['PATCH'])
def bulk_update_products(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    update = request.data.get('update')
    try:
        result = db_handle['products'].update_many(filter, {'$set': update})
        return Response({"matched_count": result.matched_count, "modified_count": result.modified_count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def product_delete(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
# Bulk Delete

@api_view(['DELETE'])
def bulk_delete_products(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    try:
        result = db_handle['products'].delete_many(filter)
        return Response({"deleted_count": result.deleted_count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Feedback

@api_view(['GET'])
def feedback_detail(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data)
    except Feedback.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def feedback_update(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        serializer = FeedbackSerializer(feedback, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Feedback.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# Bulk Update
@api_view(['PATCH'])
def bulk_update_feedbacks(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    update = request.data.get('update')
    try:
        result = db_handle['feedbacks'].update_many(filter, {'$set': update})
        return Response({"matched_count": result.matched_count, "modified_count": result.modified_count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def feedback_delete(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        feedback.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Feedback.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# Bulk Delete
@api_view(['DELETE'])
def bulk_delete_feedbacks(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    try:
        result = db_handle['feedbacks'].delete_many(filter)
        return Response({"deleted_count": result.deleted_count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Views for calling various Feedbacks to ensure the data is being stored correctly    

@api_view(['GET'])
def customer_feedbacks(request, user_id):
    """Get all feedbacks for a specific customer"""
    try:
        customer = Customer.objects.get(user_id=user_id)
        feedbacks = customer.get_feedbacks()
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def product_feedbacks(request, item_id):
    """Get all feedbacks for a specific product"""
    try:
        product = Product.objects.get(item_id=item_id)
        feedbacks = product.get_feedbacks()
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


# PyMongo Views for Advanced Functionality

# 1. Aggregation Query: Aggregate customers by waist size
@api_view(['GET'])
def customer_aggregation(request):
    """Aggregate customers by waist size."""
    db_handle, _ = get_db_handle()  # Get the PyMongo database handle
    pipeline = [
        {"$group": {"_id": "$waist", "total_customers": {"$sum": 1}}},
        {"$sort": {"total_customers": -1}}  # Sort by the number of customers
    ]
    result = list(db_handle['customers'].aggregate(pipeline))
    return Response(result)

# 2. Bulk Update: Update multiple customers' waist sizes
@api_view(['PATCH'])
def bulk_update_waist(request):
    """Bulk update customer waist sizes."""
    old_waist = request.data.get('old_waist')
    new_waist = request.data.get('new_waist')
    if not old_waist or not new_waist:
        return Response({"error": "Both 'old_waist' and 'new_waist' must be provided."},
                        status=status.HTTP_400_BAD_REQUEST)
    
    db_handle, _ = get_db_handle()  # Get the PyMongo database handle
    result = db_handle['customers'].update_many(
        {"waist": old_waist},  # Find customers with the old waist size
        {"$set": {"waist": new_waist}}  # Update the waist size
    )
    return Response({"matched_count": result.matched_count, "modified_count": result.modified_count})

# 3. Complex Filtering: Search for products by keyword
@api_view(['GET'])
def product_keyword_search(request):
    """Search for products by a specific keyword."""
    keyword = request.query_params.get('keyword', '')
    if not keyword:
        return Response({"error": "A 'keyword' query parameter must be provided."}, 
                        status=status.HTTP_400_BAD_REQUEST)

    db_handle, _ = get_db_handle()  # Get the PyMongo database handle
    result = list(db_handle['products'].find({"keywords": keyword}))
    return Response(result)
