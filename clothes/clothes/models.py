from mongoengine import Document, StringField, IntField, ListField, DateField

class Customer(Document):
    user_id = IntField(required=True, unique=True)
    user_name = StringField(max_length=100)
    waist = StringField(max_length=10)
    cup_size = StringField(max_length=5)
    bra_size = StringField(max_length=10)
    hips = StringField(max_length=10)
    bust = StringField(max_length=10)
    height = StringField(max_length=10)

class Product(Document):
    item_id = IntField(required=True, unique=True)
    product_name = StringField(max_length=100)
    size = IntField()
    quality = IntField(min_value=1, max_value=5)
    keywords = ListField(StringField(max_length=100))
    cloth_size_category = StringField(max_length=10)
    last_update_date = DateField()

class Feedback(Document):
    review_id = IntField(required=True, unique=True)
    fit = StringField(max_length=10)
    length = StringField(max_length=20)
    review_text = StringField()
    review_summary = StringField(max_length=255)
    customer_id = IntField()
    product_id = IntField()
