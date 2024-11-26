from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CustomerSerializer, ProductSerializer, FeedbackSerializer
from .models import Customer, Product, Feedback
from .utils import get_db_handle
from django.core.files.uploadedfile import UploadedFile
import json

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

# Create a new feedback
@api_view(['POST'])
def feedback_create(request):
    serializer = FeedbackSerializer(data=request.data)  # Deserialize the data
    if serializer.is_valid():
        serializer.save()  # Save the new feedback
        return Response(serializer.data, status=status.HTTP_201_CREATED)
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
