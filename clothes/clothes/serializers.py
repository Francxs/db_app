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
        if not re.match(r'^\d+(\.\d+)?$', value):
            raise ValidationError("Invalid waist measurement format.")
        return value

    def validate_height(self, value):
        """
        Validate height in the format like 5'5.
        """
        if not re.match(r'^\d\'\d+$', value):
            raise ValidationError("Invalid height format. Expected format is 5'5.")
        return value

    def validate(self, data):
        """
        Cross-field validation for waist and hips.
        """
        waist = float(data['waist'])
        hips = float(data['hips'])
        if waist >= hips:
            raise ValidationError("Waist measurement must be less than hip measurement.")
        return data

    def create(self, validated_data):
        """
        Create a new customer.
        """
        return Customer(**validated_data).save()

    def update(self, instance, validated_data):
        """
        Update an existing customer.
        """
        for key, value in validated_data.items():
            setattr(instance, key, value)
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
    Feedback data validation and serialization.
    """
    review_id = serializers.IntegerField(min_value=100000, max_value=999999)
    fit = serializers.ChoiceField(choices=['Tight', 'Loose', 'Perfect'], required=False)
    length = serializers.ChoiceField(choices=['Short', 'Regular', 'Long'], required=False)
    review_text = serializers.CharField(max_length=1000, required=False)
    review_summary = serializers.CharField(max_length=255, required=False)
    customer_id = serializers.IntegerField(source='customer.user_id')
    product_id = serializers.IntegerField(source='product.item_id')

    def to_representation(self, instance):
        """
        Customize serialized output for better JSON compatibility.
        """
        representation = super().to_representation(instance)
        return representation

    def create(self, validated_data):
        """
        Create a new Feedback instance.
        """
        validated_data['customer'] = Customer.objects.get(user_id=validated_data.pop('customer_id'))
        validated_data['product'] = Product.objects.get(item_id=validated_data.pop('product_id'))
        feedback = Feedback(**validated_data)
        feedback.clean()
        feedback.save()
        return feedback
