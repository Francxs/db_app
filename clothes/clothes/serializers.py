from rest_framework import serializers
from .models import Customer, Product, Feedback  # MongoEngine models
import re
from rest_framework.exceptions import ValidationError

class CustomerSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    user_name = serializers.CharField(max_length=100, required=True)
    waist = serializers.CharField(max_length=10, required=True)
    cup_size = serializers.CharField(max_length=5, required=True)
    bra_size = serializers.CharField(max_length=10, required=True)
    hips = serializers.CharField(max_length=10, required=True)
    bust = serializers.CharField(max_length=10, required=True)
    height = serializers.CharField(max_length=10, required=True)

    def validate_user_id(self, value):
        if not re.match(r'^\d{6}$', str(value)):
            raise ValidationError("User ID must be a 6-digit number")
        return value
    
    def validate(self, data):
        # Validate no empty strings or just whitespace
        for field in ['user_name', 'waist', 'cup_size', 'bra_size', 'hips', 'bust', 'height']:
            if not data.get(field, '').strip():
                raise serializers.ValidationError({field: "This field cannot be empty or just whitespace"})
        return data

    # Create a new Customer in MongoDB using MongoEngine
    def create(self, validated_data):
        return Customer(**validated_data).save()

    # Update an existing Customer in MongoDB using MongoEngine
    def update(self, instance, validated_data):
        instance.update(**validated_data)
        return instance.reload()

class ProductSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=True)
    product_name = serializers.CharField(max_length=100, required=True)
    size = serializers.IntegerField(required=True)
    quality = serializers.IntegerField(min_value=1, max_value=5, required=True)
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=True,
        allow_empty=False
    )
    cloth_size_category = serializers.CharField(max_length=10, required=True)
    last_update_date = serializers.DateField(required=True)

    def validate_item_id(self, value):
        if not re.match(r'^\d{6}$', str(value)):
            raise ValidationError("Item ID must be a 6-digit number")
        return value
    
    def validate_cloth_size_category(self, value):
        if value not in ['S', 'M', 'L']:
            raise serializers.ValidationError("Size category must be S, M, or L")
        return value

    def validate_keywords(self, value):
        if not value:
            raise serializers.ValidationError("Keywords list cannot be empty")
        if 'clothing' not in value:
            raise serializers.ValidationError("Keywords must include 'clothing'")
        return value

    def validate(self, data):
        # Add any cross-field validations here
        return data

    # Create a new Product in MongoDB using MongoEngine
    def create(self, validated_data):
        return Product(**validated_data).save()

    # Update an existing Product in MongoDB using MongoEngine
    def update(self, instance, validated_data):
        instance.update(**validated_data)
        return instance.reload()

class FeedbackSerializer(serializers.Serializer):
    review_id = serializers.IntegerField()
    fit = serializers.CharField(max_length=10)
    length = serializers.CharField(max_length=20, required=False)
    review_text = serializers.CharField(required=False)
    review_summary = serializers.CharField(max_length=255, required=False)
    customer_id = serializers.IntegerField()
    product_id = serializers.IntegerField()

    customer = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    def validate_review_id(self, value):
        if not re.match(r'^\d{6}$', str(value)):
            raise serializers.ValidationError("Review ID must be a 6-digit number")
        return value

    def validate_customer_id(self, value):
        if value is None:
            raise serializers.ValidationError("customer_id cannot be null")
        if not Customer.objects(user_id=value).first():
            raise serializers.ValidationError("Referenced customer does not exist")
        return value

    def validate_product_id(self, value):
        if value is None:
            raise serializers.ValidationError("product_id cannot be null")
        if not Product.objects(item_id=value).first():
            raise serializers.ValidationError("Referenced product does not exist")
        return value

    def create(self, validated_data):
        # Validate and retrieve related objects
        try:
            customer = Customer.objects.get(user_id=validated_data['customer_id'])
        except Customer.DoesNotExist:
            raise serializers.ValidationError({"customer_id": "Referenced customer does not exist"})

        try:
            product = Product.objects.get(item_id=validated_data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "Referenced product does not exist"})

        # Create and save feedback
        feedback = Feedback(
            review_id=validated_data['review_id'],
            fit=validated_data['fit'],
            length=validated_data.get('length'),
            review_text=validated_data.get('review_text'),
            review_summary=validated_data.get('review_summary'),
            customer=customer,
            product=product
        )
        feedback.save()
        return feedback

    def update(self, instance, validated_data):
        instance.update(**validated_data)
        return instance.reload()

    def get_customer(self, obj):
        """Retrieve the serialized Customer object."""
        if obj.customer:
            return CustomerSerializer(obj.customer).data
        return None

    def get_product(self, obj):
        """Retrieve the serialized Product object."""
        if obj.product:
            return ProductSerializer(obj.product).data
        return None
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['customer_id'] = instance.customer.user_id if instance.customer else None
        ret['product_id'] = instance.product.item_id if instance.product else None
        return ret


