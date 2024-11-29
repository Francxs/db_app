from mongoengine import Document, StringField, IntField, ListField, DateField, ReferenceField, CASCADE, ValidationError

class Customer(Document):
    user_id = IntField(required=True, unique=True)
    user_name = StringField(max_length=100)
    waist = StringField(max_length=10)
    cup_size = StringField(max_length=5)
    bra_size = StringField(max_length=10)
    hips = StringField(max_length=10)
    bust = StringField(max_length=10)
    height = StringField(max_length=10)

    def get_feedbacks(self):
        return Feedback.objects(customer_id=self.user_id)

class Product(Document):
    item_id = IntField(required=True, unique=True)
    product_name = StringField(max_length=100)
    size = IntField()
    quality = IntField(min_value=1, max_value=5)
    keywords = ListField(StringField(max_length=100))
    cloth_size_category = StringField(max_length=10)
    last_update_date = DateField()

    def get_feedbacks(self):
        return Feedback.objects(product_id=self.item_id)

class Feedback(Document):
    review_id = IntField(required=True, unique=True)
    fit = StringField(max_length=10)
    length = StringField(max_length=20)
    review_text = StringField()
    review_summary = StringField(max_length=255)
    customer_id = IntField()
    product_id = IntField()

    customer = ReferenceField(Customer, required=True, reverse_delete_rule=CASCADE)
    product = ReferenceField(Product, required=True, reverse_delete_rule=CASCADE)
    
    def clean(self):
        try:
            Customer.objects.get(user_id=self.customer_id)
            Product.objects.get(item_id=self.product_id)
        except:
            raise ValidationError("Referenced customer or product does not exist")
