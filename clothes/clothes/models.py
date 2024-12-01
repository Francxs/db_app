import re
from mongoengine import Document, StringField, IntField, ListField, DateField, ReferenceField, CASCADE, ValidationError, Q
from datetime import date

def validate_measurement(value):
    """
    Validates that the measurement is in the correct format.
    """
    if not re.match(r'^\d+(\.\d+)?$', value):
        raise ValidationError(f"Invalid measurement format for '{value}'.")

def validate_height(value):
    """
    Validates height format, e.g., 5'5.
    """
    if not re.match(r'^\d\'\d+$', value):
        raise ValidationError(f"Invalid height format '{value}'. Expected format is like 5'5.")

class Customer(Document):
    """
    Enhanced Customer model with robust validation and indexing.
    """
    meta = {
        'collection': 'customers',
        'indexes': [
            {'fields': ['user_id'], 'unique': True},
            {'fields': ['user_name']},
            {'fields': ['waist', 'hips', 'bust'], 'sparse': True}
        ]
    }
    
    user_id = IntField(required=True, unique=True, min_value=100000, max_value=999999)
    user_name = StringField(required=True, max_length=100, min_length=2)
    waist = StringField(required=True, max_length=10, validation=validate_measurement)
    cup_size = StringField(required=True, max_length=5, choices=['AA', 'A', 'B', 'C', 'D', 'DD', 'E', 'F', 'G'])
    bra_size = StringField(required=True, max_length=10, validation=validate_measurement)
    hips = StringField(required=True, max_length=10, validation=validate_measurement)
    bust = StringField(required=True, max_length=10, validation=validate_measurement)
    height = StringField(required=True, max_length=10, validation=validate_height)

    def clean(self):
        """
        Comprehensive validation with specific business rules.
        """
        errors = []
        
        # Validate waist vs hips measurement
        try:
            waist_val = float(self.waist)
            hips_val = float(self.hips)
            if waist_val >= hips_val:
                errors.append("Waist measurement must be less than hip measurement.")
        except ValueError:
            errors.append("Invalid measurement format for waist or hips.")
        
        if errors:
            raise ValidationError(errors)



class Product(Document):
    """
    Enhanced Product model with robust validation and indexing.
    """
    meta = {
        'collection': 'products',
        'indexes': [
            {'fields': ['item_id'], 'unique': True},
            {'fields': ['product_name'], 'sparse': True},
            {'fields': ['keywords'], 'sparse': True}
        ]
    }
    
    item_id = IntField(required=True, unique=True, min_value=100000, max_value=999999)
    product_name = StringField(required=True, max_length=100, min_length=2)
    size = IntField(required=True, min_value=0, max_value=50)
    quality = IntField(required=True, min_value=1, max_value=5)
    keywords = ListField(StringField(max_length=100), required=True, min_length=1)
    cloth_size_category = StringField(required=True, choices=['XS', 'S', 'M', 'L', 'XL', 'XXL'])
    last_update_date = DateField(required=True)

    def clean(self):
        """
        Comprehensive validation with specific business rules.
        """
        # Prevent future dates
        if self.last_update_date > date.today():
            raise ValidationError("Last update date cannot be in the future")

class Feedback(Document):
    meta = {
        'collection': 'feedback',
        'indexes': [
            {'fields': ['review_id'], 'unique': True},
            {'fields': ['customer', 'product'], 'sparse': True}
        ]
    }
    
    review_id = IntField(required=True, unique=True, min_value=100000, max_value=999999)
    fit = StringField(max_length=20)  # Removed choices
    length = StringField(max_length=20)  # Removed choices
    review_text = StringField(max_length=1000)
    review_summary = StringField(max_length=255)
    
    customer = ReferenceField(Customer, required=True, reverse_delete_rule=CASCADE)
    product = ReferenceField(Product, required=True, reverse_delete_rule=CASCADE)

    def clean(self):
        """
        Comprehensive validation with specific business rules.
        """
        # Ensure referenced documents exist
        if not self.customer or not self.product:
            raise ValidationError("Both customer and product must exist")