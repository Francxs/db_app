from rest_framework import serializers
from .models import Customer, Product, Feedback
import re
from rest_framework.exceptions import ValidationError

class CustomerSerializer(serializers.Serializer):
    """
    Light validation for Customer data before model-level validation.
    """
    user_id = serializers.IntegerField()
    user_name = serializers.CharField(max_length=100)
    waist = serializers.CharField(max_length=10)
    cup_size = serializers.CharField(max_length=5)
    bra_size = serializers.CharField(max_length=10)
    hips = serializers.CharField(max_length=10)
    bust = serializers.CharField(max_length=10)
    height = serializers.CharField(max_length=10)

    def validate_user_id(self, value):
        # Basic check to ensure user_id looks like a 6-digit number
        # Detailed validation happens in model's clean method
        if not isinstance(value, int):
            raise ValidationError("User ID must be an integer")
        return value
    
    def create(self, validated_data):
        return Customer(**validated_data).save()

    def update(self, instance, validated_data):
        instance.update(**validated_data)
        return instance.reload()

class ProductSerializer(serializers.Serializer):
    """
    Light validation for Product data before model-level validation.
    """
    item_id = serializers.IntegerField()
    product_name = serializers.CharField(max_length=100)
    size = serializers.IntegerField()
    quality = serializers.IntegerField(min_value=1, max_value=5)
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=False
    )
    cloth_size_category = serializers.CharField(max_length=10)
    last_update_date = serializers.DateField()

    def validate_item_id(self, value):
        # Basic check to ensure item_id is an integer
        # Detailed validation happens in model's clean method
        if not isinstance(value, int):
            raise ValidationError("Item ID must be an integer")
        return value
    
    def validate_cloth_size_category(self, value):
        # Light validation, with comprehensive check in model
        allowed_categories = ['S', 'M', 'L']
        if value not in allowed_categories:
            raise ValidationError(f"Size category must be one of {allowed_categories}")
        return value

    def create(self, validated_data):
        return Product(**validated_data).save()

    def update(self, instance, validated_data):
        instance.update(**validated_data)
        return instance.reload()

class FeedbackSerializer(serializers.Serializer):
    """
    Correctly serialize Feedback data, including resolving customer and product references.
    """
    review_id = serializers.IntegerField()
    fit = serializers.CharField(max_length=10, required=False)
    length = serializers.CharField(max_length=20, required=False)
    review_text = serializers.CharField(required=False)
    review_summary = serializers.CharField(max_length=255, required=False)

    # Include resolved references in the output
    customer = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    def get_customer(self, obj):
        """
        Resolve and serialize customer reference.
        """
        if obj.customer:
            return CustomerSerializer(obj.customer).data
        return None

    def get_product(self, obj):
        """
        Resolve and serialize product reference.
        """
        if obj.product:
            return ProductSerializer(obj.product).data
        return None

    def to_representation(self, instance):
        """
        Ensure customer_id and product_id are added to representation.
        """
        ret = super().to_representation(instance)
        ret['customer_id'] = instance.customer.user_id if instance.customer else None
        ret['product_id'] = instance.product.item_id if instance.product else None
        return ret
