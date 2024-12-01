import re
from mongoengine import Document, StringField, IntField, ListField, DateField, ReferenceField, CASCADE, ValidationError
from datetime import date

class Customer(Document):
    """
    Customer model with comprehensive validation.
    """
    meta = {'collection': 'customers'}
    
    user_id = IntField(required=True, unique=True)
    user_name = StringField(required=True, max_length=100)
    waist = StringField(required=True, max_length=10)
    cup_size = StringField(required=True, max_length=5)
    bra_size = StringField(required=True, max_length=10)
    hips = StringField(required=True, max_length=10)
    bust = StringField(required=True, max_length=10)
    height = StringField(required=True, max_length=10)

    def clean(self):
        """
        Comprehensive validation method for customer data.
        Runs before saving to the database.
        """
        # Validate user_id is exactly 6 digits
        if not re.match(r'^\d{6}$', str(self.user_id)):
            raise ValidationError("User ID must be a 6-digit number")
        
        # Validate non-empty fields with more specific checks
        validation_fields = {
            'user_name': (lambda x: x.strip() and len(x) <= 100, "User name must be non-empty and not exceed 100 characters"),
            'waist': (lambda x: x.strip() and len(x) <= 10, "Waist measurement must be non-empty and not exceed 10 characters"),
            'cup_size': (lambda x: x.strip() and len(x) <= 5, "Cup size must be non-empty and not exceed 5 characters"),
            'bra_size': (lambda x: x.strip() and len(x) <= 10, "Bra size must be non-empty and not exceed 10 characters"),
            'hips': (lambda x: x.strip() and len(x) <= 10, "Hips measurement must be non-empty and not exceed 10 characters"),
            'bust': (lambda x: x.strip() and len(x) <= 10, "Bust measurement must be non-empty and not exceed 10 characters"),
            'height': (lambda x: x.strip() and len(x) <= 10, "Height must be non-empty and not exceed 10 characters")
        }
        
        for field, (validator, error_msg) in validation_fields.items():
            value = getattr(self, field)
            if not validator(value):
                raise ValidationError(error_msg)

    def get_feedbacks(self):
        """
        Retrieve all feedbacks for this customer.
        """
        return Feedback.objects(customer_id=self.user_id)

class Product(Document):
    """
    Product model with comprehensive validation.
    """
    meta = {'collection': 'products'}
    
    item_id = IntField(required=True, unique=True)
    product_name = StringField(required=True, max_length=100)
    size = IntField(required=True)
    quality = IntField(required=True, min_value=1, max_value=5)
    keywords = ListField(StringField(max_length=100), required=True)
    cloth_size_category = StringField(required=True, max_length=10)
    last_update_date = DateField(required=True)

    def clean(self):
        """
        Comprehensive validation method for product data.
        Runs before saving to the database.
        """
        # Validate item_id is exactly 6 digits
        if not re.match(r'^\d{6}$', str(self.item_id)):
            raise ValidationError("Item ID must be a 6-digit number")
        
        # Validate product name
        if not self.product_name.strip() or len(self.product_name) > 100:
            raise ValidationError("Product name must be non-empty and not exceed 100 characters")
        
        # Validate keywords
        if not self.keywords or len(self.keywords) == 0:
            raise ValidationError("Keywords list cannot be empty")
        
        # Validate size category
        allowed_categories = ['S', 'M', 'L']
        if self.cloth_size_category not in allowed_categories:
            raise ValidationError(f"Size category must be one of {allowed_categories}")
        
        # Validate last update date is not in the future
        if self.last_update_date and self.last_update_date > date.today():
            raise ValidationError("Last update date cannot be in the future")

    def get_feedbacks(self):
        """
        Retrieve all feedbacks for this product.
        """
        return Feedback.objects(product_id=self.item_id)

class Feedback(Document):
    """
    Feedback model with comprehensive validation.
    """
    meta = {'collection': 'feedback'}
    
    review_id = IntField(required=True, unique=True)
    fit = StringField(max_length=10)
    length = StringField(max_length=20)
    review_text = StringField()
    review_summary = StringField(max_length=255)
    
    customer = ReferenceField(Customer, required=True, reverse_delete_rule=CASCADE)
    product = ReferenceField(Product, required=True, reverse_delete_rule=CASCADE)

    def clean(self):
        """
        Comprehensive validation method for feedback data.
        Runs before saving to the database.
        """
        # Validate review_id is exactly 6 digits
        if not re.match(r'^\d{6}$', str(self.review_id)):
            raise ValidationError("Review ID must be a 6-digit number")
        
        # Validate that customer and product references exist
        if not Customer.objects(user_id=self.customer.user_id).first():
            raise ValidationError("Referenced customer does not exist")
        
        if not Product.objects(item_id=self.product.item_id).first():
            raise ValidationError("Referenced product does not exist")
        
        # Optional field validations
        if self.fit and len(self.fit) > 10:
            raise ValidationError("Fit description cannot exceed 10 characters")
        
        if self.length and len(self.length) > 20:
            raise ValidationError("Length description cannot exceed 20 characters")
        
        if self.review_summary and len(self.review_summary) > 255:
            raise ValidationError("Review summary cannot exceed 255 characters")