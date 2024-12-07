from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CustomerSerializer, ProductSerializer, FeedbackSerializer
from .models import Customer, Product, Feedback
from .utils import get_db_handle
from django.core.files.uploadedfile import UploadedFile
import json
from rest_framework.exceptions import ValidationError
from bson import ObjectId, errors
import bson

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
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.create(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create a new product
@api_view(['POST'])
def product_create(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.create(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
# @api_view(['POST'])
# def bulk_upload_feedbacks(request):
#     """Bulk upload feedback using PyMongo."""
#     db_handle, _ = get_db_handle()  # Get the PyMongo database handle
#     try:
#         # Insert multiple feedback documents at once
#         result = db_handle['feedback'].insert_many(request.data)
#         return Response({"inserted_ids": [str(i) for i in result.inserted_ids]}, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def bulk_upload_feedbacks(request):
    """Bulk upload feedback using MongoEngine validation."""
    try:
        feedbacks_to_save = []
        for feedback_data in request.data:
            # Try to find the referenced customer and product
            try:
                customer = Customer.objects.get(user_id=feedback_data.get('customer_id'))
                product = Product.objects.get(item_id=feedback_data.get('product_id'))
                
                # Create Feedback object with proper references
                feedback = Feedback(
                    review_id=feedback_data['review_id'],
                    fit=feedback_data['fit'],
                    length=feedback_data.get('length'),
                    review_text=feedback_data.get('review_text'),
                    review_summary=feedback_data.get('review_summary'),
                    customer=customer,
                    product=product
                )
                feedbacks_to_save.append(feedback)
            except (Customer.DoesNotExist, Product.DoesNotExist):
                # Optionally, you can skip or handle documents without valid references
                print(f"Skipping feedback {feedback_data['review_id']} due to missing references")
        
        # Save all validated feedbacks
        for feedback in feedbacks_to_save:
            feedback.save()
        
        return Response({
            "inserted_count": len(feedbacks_to_save),
            "details": [f.review_id for f in feedbacks_to_save]
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




############################################################################################################
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
        customer = Customer.objects.get(user_id=customer_id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def customer_update(request, customer_id):
    try:
        customer = Customer.objects.get(id=ObjectId(customer_id))
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except (Customer.DoesNotExist, ValidationError, bson.errors.InvalidId):
        return Response({"error": "Invalid customer ID"}, status=status.HTTP_404_NOT_FOUND)
    
# Bulk Update

@api_view(['PATCH'])
def bulk_update_customers(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    update = request.data.get('update')

    if not filter or not update:
        return Response({"error": "Both 'filter' and 'update' fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if '_id' in filter:
            filter['_id'] = ObjectId(filter['_id'])
        result = db_handle['customers'].update_many(filter, {'$set': update})
        return Response({"matched_count": result.matched_count, "modified_count": result.modified_count})
    except (ValidationError, bson.errors.InvalidId) as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def customer_delete(request, customer_id):
    try:
        customer = Customer.objects.get(id=ObjectId(customer_id))
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except (Customer.DoesNotExist, ValidationError, bson.errors.InvalidId):
        return Response({"error": "Invalid customer ID"}, status=status.HTTP_404_NOT_FOUND)

# Bulk Delete
@api_view(['DELETE'])
def bulk_delete_customers(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    try:
        if '_id' in filter:
            filter['_id'] = ObjectId(filter['_id'])
        result = db_handle['customers'].delete_many(filter)
        return Response({"deleted_count": result.deleted_count})
    except (ValidationError, bson.errors.InvalidId) as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Product

@api_view(['GET'])
def product_detail(request, product_id):
    try:
        product = Product.objects.get(item_id=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def product_update(request, product_id):
    try:
        product = Product.objects.get(id=ObjectId(product_id))
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except (Product.DoesNotExist, ValidationError, bson.errors.InvalidId):
        return Response({"error": "Invalid product ID"}, status=status.HTTP_404_NOT_FOUND)

# Bulk Update
@api_view(['PATCH'])
def bulk_update_products(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    update = request.data.get('update')

    if not filter or not update:
        return Response({"error": "Both 'filter' and 'update' fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if '_id' in filter:
            filter['_id'] = ObjectId(filter['_id'])
        result = db_handle['products'].update_many(filter, {'$set': update})
        return Response({"matched_count": result.matched_count, "modified_count": result.modified_count})
    except (ValidationError, bson.errors.InvalidId) as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def product_delete(request, product_id):
    try:
        product = Product.objects.get(id=ObjectId(product_id))
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except (Product.DoesNotExist, ValidationError, bson.errors.InvalidId):
        return Response({"error": "Invalid product ID"}, status=status.HTTP_404_NOT_FOUND)
    
# Bulk Delete
@api_view(['DELETE'])
def bulk_delete_products(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    try:
        if '_id' in filter:
            filter['_id'] = ObjectId(filter['_id'])
        result = db_handle['products'].delete_many(filter)
        return Response({"deleted_count": result.deleted_count})
    except (ValidationError, bson.errors.InvalidId) as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Feedback

@api_view(['GET'])
def feedback_detail(request, feedback_id):
    user_id = request.query_params.get('user_id')
    item_id = request.query_params.get('item_id')

    try:
        feedback = Feedback.objects.get(review_id=feedback_id)

        # Debugging statements
        print(f"Feedback found: {feedback}")
        if feedback.customer:
            print(f"Feedback customer_id: {feedback.customer.user_id}")
        else:
            print("Feedback customer reference is None")

        if feedback.product:
            print(f"Feedback product_id: {feedback.product.item_id}")
        else:
            print("Feedback product reference is None")

        # Ensure feedback.customer and feedback.product are not None
        if feedback.customer is None or feedback.product is None:
            return Response({"error": "Feedback has no associated customer or product"}, status=status.HTTP_400_BAD_REQUEST)

        # Optionally filter by user_id and item_id if provided
        if user_id and feedback.customer.user_id != int(user_id):
            return Response({"error": "User ID does not match"}, status=status.HTTP_400_BAD_REQUEST)

        if item_id and feedback.product.item_id != int(item_id):
            return Response({"error": "Item ID does not match"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Exception: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PATCH'])
def feedback_update(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=ObjectId(feedback_id))
        serializer = FeedbackSerializer(feedback, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except (Feedback.DoesNotExist, ValidationError, bson.errors.InvalidId):
        return Response({"error": "Invalid feedback ID"}, status=status.HTTP_404_NOT_FOUND)

# Bulk Update
@api_view(['PATCH'])
def bulk_update_feedbacks(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    update = request.data.get('update')

    if not filter or not update:
        return Response({"error": "Both 'filter' and 'update' fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if '_id' in filter:
            filter['_id'] = ObjectId(filter['_id'])
        result = db_handle['feedback'].update_many(filter, {'$set': update})
        return Response({"matched_count": result.matched_count, "modified_count": result.modified_count})
    except (ValidationError, bson.errors.InvalidId) as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def feedback_delete(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=ObjectId(feedback_id))
        feedback.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except (Feedback.DoesNotExist, ValidationError, bson.errors.InvalidId):
        return Response({"error": "Invalid feedback ID"}, status=status.HTTP_404_NOT_FOUND)

# Bulk Delete
@api_view(['DELETE'])
def bulk_delete_feedbacks(request):
    db_handle, _ = get_db_handle()
    filter = request.data.get('filter')
    try:
        if '_id' in filter:
            filter['_id'] = ObjectId(filter['_id'])
        result = db_handle['feedbacks'].delete_many(filter)
        return Response({"deleted_count": result.deleted_count})
    except (ValidationError, bson.errors.InvalidId) as e:
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
