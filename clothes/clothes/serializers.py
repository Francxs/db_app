from rest_framework import serializers
from .models import Customer, Product, Feedback
from rest_framework.exceptions import ValidationError
import re

class CustomerSerializer(serializers.Serializer):
    """
    Enhanced customer data validation and transformation.
    """
    user_id = serializers.IntegerField(min_value=100000, max_value=999999)
    user_name = serializers.CharField(min_length=2, max_length=100)
    waist = serializers.CharField(max_length=10)
    cup_size = serializers.ChoiceField(choices=['AA', 'A', 'B', 'C', 'D', 'DD', 'E', 'F', 'G'])
    bra_size = serializers.CharField(max_length=10)
    hips = serializers.CharField(max_length=10)
    bust = serializers.CharField(max_length=10)
    height = serializers.CharField(max_length=10)

    def validate_waist(self, value):
        """
        Additional serializer-level validation for waist measurement.
        """
        if not re.match(r'^\d+(\.\d+)?[A-Za-z]?$', value):
            raise ValidationError("Invalid waist measurement format")
        return value

    def create(self, validated_data):
        """
        Custom create method with pre-save checks.
        """
        customer = Customer(**validated_data)
        customer.clean()  # Trigger model-level validation
        customer.save()
        return customer

    def update(self, instance, validated_data):
        """
        Custom update method with pre-update checks.
        """
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.clean()  # Trigger model-level validation
        instance.save()
        return instance

class ProductSerializer(serializers.Serializer):
    """
    Enhanced product data validation and transformation.
    """
    item_id = serializers.IntegerField(min_value=100000, max_value=999999)
    product_name = serializers.CharField(min_length=2, max_length=100)
    size = serializers.IntegerField(min_value=0, max_value=50)
    quality = serializers.IntegerField(min_value=1, max_value=5)
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1
    )
    cloth_size_category = serializers.ChoiceField(choices=['XS', 'S', 'M', 'L', 'XL', 'XXL'])
    last_update_date = serializers.DateField()

    def create(self, validated_data):
        """
        Custom create method with pre-save checks.
        """
        product = Product(**validated_data)
        product.clean()  # Trigger model-level validation
        product.save()
        return product

    def update(self, instance, validated_data):
        """
        Custom update method with pre-update checks.
        """
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.clean()  # Trigger model-level validation
        instance.save()
        return instance

class FeedbackSerializer(serializers.Serializer):
    """
    Enhanced feedback data validation and transformation.
    """
    review_id = serializers.IntegerField(min_value=100000, max_value=999999)
    fit = serializers.CharField(max_length=20, required=False, allow_blank=True)
    length = serializers.CharField(max_length=20, required=False, allow_blank=True)
    review_text = serializers.CharField(max_length=1000, required=False)
    review_summary = serializers.CharField(max_length=255, required=False)
    customer_id = serializers.IntegerField()
    product_id = serializers.IntegerField()

    def validate(self, data):
        """
        Cross-field validation for feedback.
        """
        # Verify customer and product exist before creating feedback
        try:
            customer = Customer.objects.get(user_id=data['customer_id'])
            product = Product.objects.get(item_id=data['product_id'])
        except (Customer.DoesNotExist, Product.DoesNotExist):
            raise ValidationError("Invalid customer or product reference")
        
        return data

    def create(self, validated_data):
        """
        Custom create method with pre-save checks.
        """
        customer = Customer.objects.get(user_id=validated_data['customer_id'])
        product = Product.objects.get(item_id=validated_data['product_id'])
        
        feedback_data = {
            'review_id': validated_data['review_id'],
            'fit': validated_data.get('fit', ''),
            'length': validated_data.get('length', ''),
            'review_text': validated_data.get('review_text', ''),
            'review_summary': validated_data.get('review_summary', ''),
            'customer': customer,
            'product': product
        }
        
        feedback = Feedback(**feedback_data)
        feedback.clean()  # Trigger model-level validation
        feedback.save()
        return feedback
