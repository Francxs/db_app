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


#############
# Create (POST)
#############


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
# Create a new feedback
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

# 1. Bulk Upload Customers (MongoEngine)
@api_view(['POST'])
def bulk_upload_customers(request):
    """Bulk upload customers using MongoEngine."""
    try:
        customers_to_save = []
        for customer_data in request.data:
            serializer = CustomerSerializer(data=customer_data)
            if serializer.is_valid():
                customers_to_save.append(Customer(**serializer.validated_data))
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Save all validated customers
        for customer in customers_to_save:
            customer.save()
        
        return Response({"inserted_ids": [str(customer.user_id) for customer in customers_to_save]}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 2. Bulk Upload Products (MongoEngine)
@api_view(['POST'])
def bulk_upload_products(request):
    """Bulk upload products using MongoEngine."""
    try:
        products_to_save = []
        for product_data in request.data:
            serializer = ProductSerializer(data=product_data)
            if serializer.is_valid():
                products_to_save.append(Product(**serializer.validated_data))
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Save all validated products
        for product in products_to_save:
            product.save()
        
        return Response({"inserted_ids": [str(product.item_id) for product in products_to_save]}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 3. Bulk Upload Feedbacks (Mongoengine)
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


#############
# Read (GET)
#############


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
    """
    Retrieve a list of all feedbacks.
    """
    try:
        feedbacks = Feedback.objects.all()
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def customer_detail(request, customer_id):
    """
    Retrieve details of a specific customer.
    
    Args:
    - customer_id: ID of the customer to retrieve
    
    Returns:
    - Customer details if found
    - 404 Not Found if customer doesn't exist
    """
    try:
        customer = Customer.objects.get(user_id=customer_id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def product_detail(request, product_id):
    """
    Retrieve details of a specific product.
    
    Args:
    - product_id: ID of the product to retrieve
    
    Returns:
    - Product details if found
    - 404 Not Found if product doesn't exist
    """
    try:
        product = Product.objects.get(item_id=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def feedback_detail(request, feedback_id):
    """
    Retrieve details of a specific feedback, including associated customer and product details.
    """
    try:
        # Retrieve the feedback
        feedback = Feedback.objects.get(review_id=feedback_id)
        
        # Serialize the feedback
        serializer = FeedbackSerializer(feedback)
        
        # Get the associated customer and product
        customer = feedback.customer
        product = feedback.product
        
        # Serialize customer and product details
        customer_serializer = CustomerSerializer(customer)
        product_serializer = ProductSerializer(product)
        
        # Create a response dictionary with all details
        response_data = serializer.data
        response_data['customer'] = customer_serializer.data
        response_data['product'] = product_serializer.data
        
        return Response(response_data)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

# Views for calling various Feedbacks to ensure the data is being stored correctly 

@api_view(['GET'])
def customer_feedbacks(request, user_id):
    """
    Retrieve all feedback IDs for a specific customer.
    
    Args:
    - user_id: ID of the customer
    
    Returns:
    - List of customer's feedback review IDs
    - 404 Not Found if customer doesn't exist
    """
    try:
        customer = Customer.objects.get(user_id=user_id)
        # Explicitly query for review IDs associated with this customer
        feedbacks = Feedback.objects.filter(customer=customer)
        # Extract just the review IDs
        feedback_ids = [feedback.review_id for feedback in feedbacks]
        return Response({"feedback_ids": feedback_ids})
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def product_feedbacks(request, item_id):
    """
    Retrieve all feedback IDs for a specific product.
    
    Args:
    - item_id: ID of the product
    
    Returns:
    - List of product's feedback review IDs
    - 404 Not Found if product doesn't exist
    """
    try:
        product = Product.objects.get(item_id=item_id)
        # Explicitly query for review IDs associated with this product
        feedbacks = Feedback.objects.filter(product=product)
        # Extract just the review IDs
        feedback_ids = [feedback.review_id for feedback in feedbacks]
        return Response({"feedback_ids": feedback_ids})
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


#############
# Update (PATCH)
#############


@api_view(['PATCH'])
def customer_update(request, customer_id):
    """
    Update a specific customer's details.
    
    Args:
    - customer_id: ID of the customer to update
    
    Returns:
    - Updated customer details if successful
    - 400 Bad Request if validation fails
    - 404 Not Found if customer doesn't exist
    """
    try:
        customer = Customer.objects.get(id=ObjectId(customer_id))
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except (Customer.DoesNotExist, ValidationError, bson.errors.InvalidId):
        return Response({"error": "Invalid customer ID"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def bulk_update_customers(request):
    """
    Bulk update customers matching specific filter criteria.
    
    Args:
    - filter: Criteria to select customers
    - update: Data to update matching customers
    
    Returns:
    - Count of matched and modified customers
    - 400 Bad Request if filter or update is missing
    """
    filter_data = request.data.get('filter', {})
    update_data = request.data.get('update', {})

    if not filter_data or not update_data:
        return Response({"error": "Both 'filter' and 'update' fields are required"}, 
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get matched customers
        matched_count = Customer.objects.filter(**filter_data).count()

        if matched_count == 0:
            return Response({"matched_count": 0, "modified_count": 0})

        # Perform bulk update
        modified_count = Customer.objects.filter(**filter_data).update(**update_data)

        return Response({
            "matched_count": matched_count,
            "modified_count": modified_count
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def product_update(request, product_id):
    """
    Update a specific product's details.
    
    Args:
    - product_id: ID of the product to update
    
    Returns:
    - Updated product details if successful
    - 400 Bad Request if validation fails
    - 404 Not Found if product doesn't exist
    """
    try:
        product = Product.objects.get(id=ObjectId(product_id))
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except (Product.DoesNotExist, ValidationError, bson.errors.InvalidId):
        return Response({"error": "Invalid product ID"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def bulk_update_products(request):
    """
    Bulk update products matching specific filter criteria.
    """
    filter_data = request.data.get('filter', {})
    update_data = request.data.get('update', {})

    if not filter_data or not update_data:
        return Response({"error": "Both 'filter' and 'update' fields are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        # Count matched documents before updating
        matched_count = Product.objects.filter(**filter_data).count()

        if matched_count == 0:
            return Response({"matched_count": 0, "modified_count": 0})

        # Perform bulk update
        modified_count = Product.objects.filter(**filter_data).update(**update_data)

        return Response({
            "matched_count": matched_count,
            "modified_count": modified_count
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def feedback_update(request, feedback_id):
    """
    Update a specific feedback's details.
    """
    try:
        feedback = Feedback.objects.get(review_id=feedback_id)
        serializer = FeedbackSerializer(feedback, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def bulk_update_feedbacks(request):
    """
    Bulk update feedback matching specific filter criteria.
    """
    filter_data = request.data.get('filter', {})
    update_data = request.data.get('update', {})

    if not filter_data or not update_data:
        return Response({"error": "Both 'filter' and 'update' fields are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        # Count matched documents before updating
        matched_count = Feedback.objects.filter(**filter_data).count()

        if matched_count == 0:
            return Response({"matched_count": 0, "modified_count": 0})

        # Perform bulk update
        modified_count = Feedback.objects.filter(**filter_data).update(**update_data)

        return Response({
            "matched_count": matched_count,
            "modified_count": modified_count
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#############
# Update (PATCH)
#############


# DELETE: Customer Delete
@api_view(['DELETE'])
def customer_delete(request, customer_id):
    """
    Delete a specific customer by ID.
    """
    try:
        customer = Customer.objects.get(user_id=customer_id)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

# DELETE: Product Delete
@api_view(['DELETE'])
def product_delete(request, product_id):
    """
    Delete a specific product by ID.
    """
    try:
        product = Product.objects.get(item_id=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

# DELETE: Feedback Delete
@api_view(['DELETE'])
def feedback_delete(request, feedback_id):
    """
    Delete a specific feedback by ID.
    """
    try:
        feedback = Feedback.objects.get(review_id=feedback_id)
        feedback.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)

# DELETE: Bulk Delete Customers
@api_view(['DELETE'])
def bulk_delete_customers(request):
    """
    Bulk delete customers matching specific criteria.
    """
    filter_data = request.data.get('filter', {})
    try:
        deleted_count_tuple = Customer.objects.filter(**filter_data).delete()
        deleted_count = deleted_count_tuple[0] if isinstance(deleted_count_tuple, tuple) else deleted_count_tuple
        return Response({"deleted_count": deleted_count}, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# DELETE: Bulk Delete Products
@api_view(['DELETE'])
def bulk_delete_products(request):
    """
    Bulk delete products matching specific criteria.
    """
    filter_data = request.data.get('filter', {})
    try:
        deleted_count_tuple = Product.objects.filter(**filter_data).delete()
        deleted_count = deleted_count_tuple[0] if isinstance(deleted_count_tuple, tuple) else deleted_count_tuple
        return Response({"deleted_count": deleted_count}, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# DELETE: Bulk Delete Feedbacks
@api_view(['DELETE'])
def bulk_delete_feedbacks(request):
    """
    Bulk delete feedbacks matching specific criteria.
    """
    filter_data = request.data.get('filter', {})
    try:
        deleted_count_tuple = Feedback.objects.filter(**filter_data).delete()
        deleted_count = deleted_count_tuple[0] if isinstance(deleted_count_tuple, tuple) else deleted_count_tuple
        return Response({"deleted_count": deleted_count}, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
