import re
from mongoengine import Document, StringField, IntField, ListField, DateField, ReferenceField, CASCADE, ValidationError

class Customer(Document):
    meta = {'collection': 'customers'}  # Explicitly specify the collection name
    user_id = IntField(required=True, unique=True)
    user_name = StringField(max_length=100)
    waist = StringField(max_length=10)
    cup_size = StringField(max_length=5)
    bra_size = StringField(max_length=10)
    hips = StringField(max_length=10)
    bust = StringField(max_length=10)
    height = StringField(max_length=10)

    def clean(self):
        if not re.match(r'^\d{6}$', str(self.user_id)):
            raise ValidationError("User ID must be a 6-digit number")

    def get_feedbacks(self):
        return Feedback.objects(customer_id=self.user_id)

class Product(Document):
    meta = {'collection': 'products'}  # Explicitly specify the collection name
    item_id = IntField(required=True, unique=True)
    product_name = StringField(max_length=100)
    size = IntField()
    quality = IntField(min_value=1, max_value=5)
    keywords = ListField(StringField(max_length=100))
    cloth_size_category = StringField(max_length=10)
    last_update_date = DateField()

    def clean(self):
        if not re.match(r'^\d{6}$', str(self.item_id)):
            raise ValidationError("Item ID must be a 6-digit number")

    def get_feedbacks(self):
        return Feedback.objects(product_id=self.item_id)

class Feedback(Document):
    meta = {'collection': 'feedback'}  # Explicitly specify the collection name
    review_id = IntField(required=True, unique=True)
    fit = StringField(max_length=10)
    length = StringField(max_length=20)
    review_text = StringField()
    review_summary = StringField(max_length=255)
    customer_id = IntField()
    product_id = IntField()

    customer = ReferenceField(Customer, required=True, reverse_delete_rule=CASCADE)
    product = ReferenceField(Product, required=True, reverse_delete_rule=CASCADE)

    # def clean(self):
    #     if not Customer.objects(user_id=self.customer_id).first():
    #         raise ValidationError("Referenced customer does not exist")
    #     if not Product.objects(item_id=self.product_id).first():
    #         raise ValidationError("Referenced product does not exist")
    
    def clean(self):
        pass  # Bypass model validation to avoid duplication with serializers
