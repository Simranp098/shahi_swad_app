from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# -------------------------------------------------------------------
# 1. CATEGORIES & MENU ITEMS WITH MULTI-PORTION PRICING
# -------------------------------------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    display_order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    FOOD_TYPE_CHOICES = (
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
        ('EGG', 'Egg'),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=150)
    food_type = models.CharField(max_length=10, choices=FOOD_TYPE_CHOICES, default='VEG')
    
    # Base / Single portion price
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Default or Single portion price")
    
    # Multi-portion pricing (P = Plate, H = Half, F = Full)
    plate_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Plate portion price (P)")
    half_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Half portion price (H)")
    full_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Full portion price (F)")
    
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def has_multiple_portions(self):
        """Returns True if item has portion choices (Plate, Half, or Full)."""
        return bool(self.plate_price or self.half_price or self.full_price)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


# -------------------------------------------------------------------
# 2. CUSTOMER & DELIVERY ADDRESS
# -------------------------------------------------------------------
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True, help_text="Used for PIN recovery")
    address = models.TextField(blank=True, null=True, help_text="Full street address and landmark for delivery")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.mobile_number})"


# -------------------------------------------------------------------
# 3. ORDERS & ORDER ITEMS
# -------------------------------------------------------------------
class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('RECEIVED', 'Order Received'),
        ('PREPARING', 'Preparing in Kitchen'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('UPI', 'Online Payment (PhonePe/UPI)'),
        ('COD', 'Cash on Delivery'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('UNPAID', 'Unpaid'),
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    order_id = models.CharField(max_length=20, default='SS-000000', editable=False)
    customer_name = models.CharField(max_length=100, default='Guest')
    mobile_number = models.CharField(max_length=15, default='0000000000')
    delivery_address = models.TextField(default='N/A')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='RECEIVED')
    
    # PhonePe Payment Tracking Fields
    merchant_transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text="PhonePe Merchant Txn ID")
    provider_reference_id = models.CharField(max_length=100, blank=True, null=True, help_text="PhonePe Provider Txn ID")
    upi_txn_ref = models.CharField(max_length=100, blank=True, null=True, help_text="Transaction reference for UPI")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id or self.order_id == 'SS-000000':
            import uuid
            self.order_id = f"SS-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name} (₹{self.total_amount})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=150, default='Food Item')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    portion = models.CharField(max_length=20, default='Standard', help_text="e.g. Single, Plate, Half, Full")

    def get_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.item_name} ({self.portion})"


# -------------------------------------------------------------------
# 4. MARQUEE ANNOUNCEMENTS & OFFERS
# -------------------------------------------------------------------
class OfferBanner(models.Model):
    message = models.CharField(max_length=255, help_text="e.g. Free home delivery within 3 km on orders above ₹300!")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Banner: {self.message} ({'Active' if self.is_active else 'Inactive'})"


# -------------------------------------------------------------------
# 5. CUSTOMER SERVICE RATING & REVIEWS
# -------------------------------------------------------------------
class ServiceRating(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='rating')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating: {self.rating}/5 for Order {self.order.order_id}"


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('General Inquiry', 'General Inquiry'),
        ('Bulk Order / Catering', 'Bulk Order / Catering'),
        ('Feedback & Suggestions', 'Feedback & Suggestions'),
        ('Delivery Help', 'Delivery Help'),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='General Inquiry')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%d %b %Y')})"