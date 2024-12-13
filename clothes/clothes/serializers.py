from rest_framework import serializers
from .models import Customer, Product, Feedback
from rest_framework.exceptions import ValidationError
import re
from datetime import timedelta, date

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
        Enhanced waist measurement validation
        - Ensure numeric value
        - Add range constraints (e.g., typical waist sizes)
        """
        try:
            waist_val = float(value)
            if waist_val < 20 or waist_val > 60:
                raise ValidationError("Waist measurement seems unusual. Expected between 20-60 inches.")
        except ValueError:
            raise ValidationError("Waist must be a numeric value.")
        return value

    def validate_bra_size(self, value):
        """
        Enhanced bra size validation
        - Ensure band size is even number between 28-52
        - Validate format (numeric + optional letter)
        """
        if not re.match(r'^(28|30|32|34|36|38|40|42|44|46|48|50|52)(?:[A-D]{0,1})?$', value):
            raise ValidationError("Invalid bra size. Use format like '34B' or '36'.")
        return value

    def validate_height(self, value):
        """
        Enhanced height validation
        - Ensure feet and inches are within reasonable ranges
        """
        match = re.match(r'^(\d)\'(\d{1,2})$', value)
        if not match:
            raise ValidationError("Height must be in format 5'6")
        
        feet, inches = int(match.group(1)), int(match.group(2))
        if feet < 4 or feet > 7 or inches > 11:
            raise ValidationError("Height seems unusual. Expected between 4'0 and 7'11")
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

    def validate_keywords(self, value):
        """
        Enhanced keyword validation
        - Ensure keywords are meaningful
        - Limit number of keywords
        - Normalize keywords
        """
        if len(value) > 5:
            raise ValidationError("Maximum 5 keywords allowed.")
        
        # Normalize and clean keywords
        cleaned_keywords = [
            keyword.lower().strip() 
            for keyword in value 
            if keyword.strip()
        ]
        
        # Optional: Check against a predefined list of valid product categories
        valid_categories = [
            'clothing', 'accessories', 'tops', 'bottoms', 'dresses', 
            'underwear', 'sportswear', 'formal', 'casual', 'shoes'
        ]
        
        for keyword in cleaned_keywords:
            if keyword not in valid_categories:
                raise ValidationError(f"Keyword '{keyword}' is not a valid product category.")
        
        return cleaned_keywords
    
    def validate_last_update_date(self, value):
        """
        Enhanced date validation
        - Prevent future dates
        - Ensure reasonable update window
        """
        if value > date.today():
            raise ValidationError("Update date cannot be in the future.")
        
        max_past_date = date.today() - timedelta(days=365 * 5)  # 5 years
        if value < max_past_date:
            raise ValidationError("Update date seems too old. Maximum 5 years in the past.")
        
        return value

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

    def validate_review_text(self, value):
        """
        Enhanced review text validation
        - Detect potential spam or meaningless reviews
        - Enforce minimum meaningful content
        """
        # Remove whitespace
        cleaned_text = value.strip()
        
        # Check for minimum meaningful length
        if len(cleaned_text) < 10:
            raise ValidationError("Review text is too short to be meaningful.")
        
        # Optional: Basic spam detection
        spam_keywords = ['buy now', 'click here', 'free']
        if any(keyword.lower() in cleaned_text.lower() for keyword in spam_keywords):
            raise ValidationError("Review appears to contain spam-like content.")
        
        return cleaned_text

    def validate(self, data):
        """
        Cross-field validation for feedback
        """
        # Ensure review text and summary don't contradict
        if 'review_text' in data and 'review_summary' in data:
            text_lower = data['review_text'].lower()
            summary_lower = data['review_summary'].lower()
            
            # Basic inconsistency check
            if len(summary_lower) > len(text_lower):
                raise ValidationError("Review summary cannot be longer than review text.")
        
        return data

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
