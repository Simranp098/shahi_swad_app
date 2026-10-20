import json
import random
import base64
import hashlib
import uuid
import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import (
    Category, MenuItem, Order, OrderItem, OfferBanner, 
    CustomerProfile, ServiceRating, ContactMessage
)

# Hotel Base Coordinates (Chhatrapati Sambhajinagar)
HOTEL_LAT = 20.0385
HOTEL_LNG = 75.4055


# -------------------------------------------------------------------
# PHONEPE HELPER FUNCTIONS & API INTEGRATION
# -------------------------------------------------------------------
def generate_phonepe_checksum(base64_payload, endpoint, salt_key, salt_index):
    """Generates SHA256 X-VERIFY checksum signature for PhonePe Gateway API requests."""
    string_to_hash = base64_payload + endpoint + salt_key
    sha256_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
    return f"{sha256_hash}###{salt_index}"


def initiate_phonepe_payment_session(order):
    """Generates payload and requests PhonePe payment URL for customer checkout."""
    try:
        merchant_txn_id = f"TXN_{order.order_id}_{uuid.uuid4().hex[:6].upper()}"
        order.merchant_transaction_id = merchant_txn_id
        order.payment_status = 'PENDING'
        order.save()

        # PhonePe requires amount in Paise (e.g. ₹100 = 10000)
        amount_in_paise = int(order.total_amount * 100)

        # Fallback Sandbox Credentials from settings
        merchant_id = getattr(settings, 'PHONEPE_MERCHANT_ID', 'PGTESTPAYUAT')
        salt_key = getattr(settings, 'PHONEPE_SALT_KEY', '099eb0cd-02cf-4e2a-8aca-3e6c6aff0399')
        salt_index = getattr(settings, 'PHONEPE_SALT_INDEX', '1')
        pay_url = getattr(settings, 'PHONEPE_PAY_URL', 'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay')
        redirect_url = getattr(settings, 'PHONEPE_REDIRECT_URL', 'http://127.0.0.1:8000/payments/phonepe/response/')
        callback_url = getattr(settings, 'PHONEPE_CALLBACK_URL', 'http://127.0.0.1:8000/payments/phonepe/webhook/')

        payload = {
            "merchantId": merchant_id,
            "merchantTransactionId": merchant_txn_id,
            "merchantUserId": f"CUST_{order.mobile_number}",
            "amount": amount_in_paise,
            "redirectUrl": redirect_url,
            "redirectMode": "POST",
            "callbackUrl": callback_url,
            "mobileNumber": order.mobile_number,
            "paymentInstrument": {
                "type": "PAY_PAGE"
            }
        }

        json_payload = json.dumps(payload)
        base64_payload = base64.b64encode(json_payload.encode('utf-8')).decode('utf-8')

        checksum = generate_phonepe_checksum(
            base64_payload, 
            "/pg/v1/pay", 
            salt_key, 
            salt_index
        )

        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum
        }

        request_body = {
            "request": base64_payload
        }

        response = requests.post(pay_url, json=request_body, headers=headers, timeout=10)
        res_data = response.json()

        if res_data.get("success") and "data" in res_data:
            return res_data["data"]["instrumentResponse"]["redirectInfo"]["url"]
        return None
    except Exception as e:
        print("PhonePe Gateway Initiation Error:", str(e))
        return None


@csrf_exempt
def phonepe_response(request):
    """Handles browser redirect from PhonePe after payment attempt."""
    merchant_txn_id = request.POST.get("merchantTransactionId") or request.GET.get("merchantTransactionId")
    code = request.POST.get("code") or request.GET.get("code")

    order = Order.objects.filter(merchant_transaction_id=merchant_txn_id).first()

    if code == "PAYMENT_SUCCESS":
        if order:
            order.payment_status = 'PAID'
            order.save()
        status_flag = 'payment_success'
    else:
        if order:
            order.payment_status = 'FAILED'
            order.save()
        status_flag = 'payment_failed'

    context = {
        'order': order,
        status_flag: True,
        'hotel_phone': '+91 9175348484',
        'hotel_email': 'Hotel.shahi.swad@gmail.com',
        'hotel_address': 'Gut No. 182, Naigavhan, Tal. Phulambri, Dist. Chhatrapati Sambhajinagar',
    }
    return render(request, 'receipt.html', context)


@csrf_exempt
def phonepe_webhook(request):
    """Real-time server-to-server callback from PhonePe upon payment completion."""
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            encoded_response = payload.get("response")

            # Decode Base64 encrypted callback payload
            decoded_bytes = base64.b64decode(encoded_response)
            decoded_json = json.loads(decoded_bytes.decode('utf-8'))

            if decoded_json.get("success"):
                txn_data = decoded_json.get("data", {})
                merchant_txn_id = txn_data.get("merchantTransactionId")
                provider_ref_id = txn_data.get("transactionId")

                order = Order.objects.filter(merchant_transaction_id=merchant_txn_id).first()
                if order:
                    order.payment_status = 'PAID'
                    order.provider_reference_id = provider_ref_id
                    order.save()
                    return JsonResponse({"status": "SUCCESS", "message": "Order payment verified"})

        except Exception as e:
            return JsonResponse({"status": "ERROR", "message": str(e)}, status=400)

    return JsonResponse({"status": "INVALID_REQUEST"}, status=400)


# -------------------------------------------------------------------
# CUSTOMER WEB APPLICATION VIEWS
# -------------------------------------------------------------------
def customer_menu(request):
    """Renders main customer web application with user session context."""
    categories = Category.objects.prefetch_related('items').all()
    active_banners = OfferBanner.objects.filter(is_active=True).order_by('-created_at')
    
    if request.user.is_authenticated:
        customer_mobile = request.user.username
        try:
            profile = request.user.profile
            customer_name = profile.name or request.user.first_name
            customer_address = profile.address or ''
        except CustomerProfile.DoesNotExist:
            customer_name = request.user.first_name or 'Valued Customer'
            customer_address = ''
    else:
        customer_mobile = request.session.get('customer_mobile', '')
        customer_name = request.session.get('customer_name', '')
        customer_address = request.session.get('customer_address', '')

    context = {
        'categories': categories,
        'active_banners': active_banners,
        'customer_name': customer_name,
        'customer_mobile': customer_mobile,
        'customer_address': customer_address,
        'upi_id': '8766595706@ybl',
        'hotel_phone': '+91 9175348484',
        'hotel_email': 'Hotel.shahi.swad@gmail.com',
        'hotel_address': 'Gut No. 182, Naigavhan, Tal. Phulambri, Dist. Chhatrapati Sambhajinagar',
    }
    return render(request, 'index.html', context)


@csrf_exempt
def check_mobile_api(request):
    """Checks whether a mobile number is already registered."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile', '').strip()

            if not mobile or len(mobile) != 10 or not mobile.isdigit():
                return JsonResponse({'status': 'error', 'message': 'Please enter a valid 10-digit mobile number'}, status=400)

            user_exists = User.objects.filter(username=mobile).exists()
            user_name = ""
            user_address = ""
            
            if user_exists:
                profile = CustomerProfile.objects.filter(mobile_number=mobile).first()
                if profile:
                    user_name = profile.name
                    user_address = profile.address or ""

            return JsonResponse({
                'status': 'success',
                'is_existing': user_exists,
                'user_name': user_name,
                'user_address': user_address
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def register_pin_api(request):
    """Registers a new user with Mobile Number, Name, Email, and a 4-Digit PIN."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile', '').strip()
            pin = data.get('pin', '').strip()
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            address = data.get('address', '').strip()

            if not mobile or len(mobile) != 10 or not mobile.isdigit():
                return JsonResponse({'status': 'error', 'message': 'Please enter a valid 10-digit mobile number'}, status=400)
            if not pin or len(pin) != 4 or not pin.isdigit():
                return JsonResponse({'status': 'error', 'message': 'PIN must be a 4-digit number'}, status=400)
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Please enter your name'}, status=400)

            if User.objects.filter(username=mobile).exists():
                return JsonResponse({'status': 'error', 'message': 'Mobile number already registered. Please sign in.'}, status=400)

            user = User.objects.create_user(
                username=mobile,
                password=pin,
                first_name=name,
                email=email
            )

            profile, _ = CustomerProfile.objects.update_or_create(
                mobile_number=mobile,
                defaults={'user': user, 'name': name, 'email': email, 'address': address}
            )

            login(request, user)
            request.session['customer_mobile'] = mobile
            request.session['customer_name'] = name
            request.session['customer_address'] = address

            return JsonResponse({
                'status': 'success',
                'message': 'Account registered successfully!',
                'mobile': mobile,
                'name': name,
                'address': address
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def login_pin_api(request):
    """Authenticates existing user with Mobile Number and 4-Digit PIN."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile', '').strip()
            pin = data.get('pin', '').strip()

            if not mobile or not pin:
                return JsonResponse({'status': 'error', 'message': 'Please enter both Mobile Number and PIN'}, status=400)

            user = authenticate(request, username=mobile, password=pin)

            if user is not None:
                login(request, user)
                
                try:
                    profile = user.profile
                    name = profile.name
                    address = profile.address or ''
                except CustomerProfile.DoesNotExist:
                    name = user.first_name or 'Valued Customer'
                    address = ''

                request.session['customer_mobile'] = mobile
                request.session['customer_name'] = name
                request.session['customer_address'] = address

                return JsonResponse({
                    'status': 'success',
                    'message': 'Logged in successfully!',
                    'mobile': mobile,
                    'name': name,
                    'address': address
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Incorrect 4-Digit PIN or Mobile Number'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def logout_api(request):
    """Logs out the user and clears session data."""
    logout(request)
    request.session.flush()
    return JsonResponse({'status': 'success', 'message': 'Logged out successfully!'})


@csrf_exempt
def request_pin_reset_api(request):
    """Sends a 6-digit OTP code to the user's email address for PIN recovery."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            identifier = data.get('identifier', '').strip() or data.get('mobile', '').strip() or data.get('email', '').strip()
            input_email = data.get('email', '').strip()

            if not identifier:
                return JsonResponse({'status': 'error', 'message': 'Please enter your Username, Mobile Number, or Email.'}, status=400)

            user = User.objects.filter(username__iexact=identifier).first()
            if not user:
                user = User.objects.filter(email__iexact=identifier).first()
            if not user:
                profile = CustomerProfile.objects.filter(mobile_number=identifier).first()
                if profile and profile.user:
                    user = profile.user

            if not user:
                return JsonResponse({'status': 'error', 'message': 'No account found matching the provided details.'}, status=404)

            profile = getattr(user, 'profile', None) or CustomerProfile.objects.filter(user=user).first()
            registered_email = user.email or (profile.email if profile else None)

            if input_email and registered_email and input_email.lower() != registered_email.lower():
                return JsonResponse({'status': 'error', 'message': 'Email does not match our records for this account.'}, status=400)

            target_email = registered_email or input_email
            if not target_email:
                return JsonResponse({'status': 'error', 'message': 'No email address registered for this account.'}, status=400)

            reset_otp = str(random.randint(100000, 999999))
            request.session['reset_otp'] = reset_otp
            request.session['reset_user_id'] = user.id

            subject = 'Hotel Shahi Swad - Security Verification Code'
            message = (
                f'Hello {user.first_name or user.username},\n\n'
                f'Your 6-digit verification code to reset your password/PIN is: {reset_otp}\n\n'
                f'Please enter this code on the password reset screen.'
            )
            
            try:
                send_mail(subject, message, None, [target_email], fail_silently=False)
            except Exception as mail_err:
                return JsonResponse({'status': 'error', 'message': f'Failed to send email. Error: {str(mail_err)}'}, status=500)

            masked_email = target_email
            if '@' in target_email:
                parts = target_email.split('@')
                if len(parts[0]) > 2:
                    masked_email = parts[0][0] + '***' + parts[0][-1] + '@' + parts[1]

            return JsonResponse({
                'status': 'success',
                'message': f'Verification OTP sent to {masked_email}',
                'target_email': masked_email
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def verify_and_reset_pin_api(request):
    """Verifies reset OTP and sets the new 4-digit PIN."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_otp = data.get('otp', '').strip()
            new_pin = data.get('new_pin', '').strip() or data.get('new_password', '').strip()

            session_otp = request.session.get('reset_otp')
            reset_user_id = request.session.get('reset_user_id')
            reset_mobile = request.session.get('reset_mobile')

            if not session_otp:
                return JsonResponse({'status': 'error', 'message': 'Reset session expired. Please request a new OTP.'}, status=400)

            if user_otp != session_otp:
                return JsonResponse({'status': 'error', 'message': 'Invalid verification OTP code.'}, status=400)

            if not new_pin or len(new_pin) < 4:
                return JsonResponse({'status': 'error', 'message': 'New password/PIN must be at least 4 characters long.'}, status=400)

            user = None
            if reset_user_id:
                user = User.objects.filter(id=reset_user_id).first()
            elif reset_mobile:
                user = User.objects.filter(username=reset_mobile).first()

            if not user:
                return JsonResponse({'status': 'error', 'message': 'User account not found.'}, status=404)

            user.set_password(new_pin)
            user.save()

            request.session.pop('reset_otp', None)
            request.session.pop('reset_user_id', None)
            request.session.pop('reset_mobile', None)

            return JsonResponse({'status': 'success', 'message': 'Password / PIN updated successfully! You can now log in.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def update_profile_api(request):
    """Updates customer profile details (Name, Address, Email)."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = request.user.username if request.user.is_authenticated else (request.session.get('customer_mobile') or data.get('mobile'))
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            address = data.get('address', '').strip()

            if not mobile:
                return JsonResponse({'status': 'error', 'message': 'Session expired. Please sign in again.'}, status=401)

            defaults = {}
            if name:
                defaults['name'] = name
                if request.user.is_authenticated:
                    request.user.first_name = name
                    request.user.save()
            if email:
                defaults['email'] = email
                if request.user.is_authenticated:
                    request.user.email = email
                    request.user.save()
            if address:
                defaults['address'] = address

            profile, _ = CustomerProfile.objects.update_or_create(
                mobile_number=mobile,
                defaults=defaults
            )

            request.session['customer_mobile'] = profile.mobile_number
            request.session['customer_name'] = profile.name
            request.session['customer_address'] = profile.address or ''

            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated successfully!',
                'mobile': profile.mobile_number,
                'name': profile.name,
                'email': profile.email or '',
                'address': profile.address or ''
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_order_history_api(request):
    """Returns past orders for authenticated or session user."""
    mobile = request.user.username if request.user.is_authenticated else (request.session.get('customer_mobile') or request.GET.get('mobile'))
    if not mobile:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=401)

    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')[:20]
    else:
        orders = Order.objects.filter(mobile_number=mobile).order_by('-created_at')[:20]

    orders_data = []
    for order in orders:
        items_data = [
            {'name': item.item_name, 'qty': item.quantity, 'price': float(item.price), 'portion': item.portion}
            for item in order.items.all()
        ]
        has_rated = ServiceRating.objects.filter(order=order).exists()
        orders_data.append({
            'order_id': order.order_id,
            'date': order.created_at.strftime('%d %b %Y, %I:%M %p'),
            'total_amount': float(order.total_amount),
            'order_status': order.order_status,
            'order_status_display': order.get_order_status_display(),
            'payment_status': order.get_payment_status_display(),
            'payment_method': order.get_payment_method_display(),
            'has_rated': has_rated,
            'items': items_data
        })

    return JsonResponse({'status': 'success', 'orders': orders_data})


@csrf_exempt
def active_orders_api(request):
    """Returns active and recent orders for background polling."""
    mobile = request.user.username if request.user.is_authenticated else (request.session.get('customer_mobile') or request.GET.get('mobile'))
    if not mobile:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=401)

    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        orders = Order.objects.filter(mobile_number=mobile).order_by('-created_at')[:5]

    orders_data = []
    for order in orders:
        has_rated = ServiceRating.objects.filter(order=order).exists()
        orders_data.append({
            'order_id': order.order_id,
            'order_status': order.order_status,
            'order_status_display': order.get_order_status_display(),
            'has_rated': has_rated,
            'total_amount': float(order.total_amount),
            'payment_method': order.get_payment_method_display(),
            'created_at': order.created_at.strftime('%d %b %Y, %I:%M %p')
        })

    return JsonResponse({'status': 'success', 'orders': orders_data})


@csrf_exempt
def place_order_api(request):
    """Processes checkout and creates a new order linked to user profile with PhonePe PG support."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            mobile = data.get('mobile')
            address = data.get('address')
            payment_method = data.get('payment_method', 'COD')
            cart = data.get('cart', [])

            if not cart or not name or not mobile or not address:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            request.session['customer_name'] = name
            request.session['customer_mobile'] = mobile
            request.session['customer_address'] = address

            profile, _ = CustomerProfile.objects.update_or_create(
                mobile_number=mobile,
                defaults={'name': name, 'address': address}
            )

            total = sum(float(item['price']) * int(item['quantity']) for item in cart)

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else profile.user,
                customer_name=name,
                mobile_number=mobile,
                delivery_address=address,
                payment_method=payment_method,
                payment_status='PENDING' if payment_method in ['UPI', 'ONLINE'] else 'UNPAID',
                total_amount=total,
                order_status='RECEIVED'
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    item_name=item['name'],
                    quantity=item['quantity'],
                    price=item['price'],
                    portion=item.get('portion', 'Standard')
                )

            # --- PhonePe Gateway Online Payment Execution ---
            if payment_method in ['UPI', 'ONLINE']:
                pay_url = initiate_phonepe_payment_session(order)
                if pay_url:
                    return JsonResponse({
                        'status': 'success',
                        'order_id': order.order_id,
                        'total_amount': float(order.total_amount),
                        'payment_method': 'ONLINE',
                        'pay_url': pay_url
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Failed to initiate PhonePe Gateway session. Please try Cash on Delivery.'
                    }, status=500)

            # Cash on Delivery Flow
            return JsonResponse({
                'status': 'success',
                'order_id': order.order_id,
                'total_amount': float(order.total_amount),
                'payment_method': 'COD'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def submit_rating_api(request):
    """Handles service ratings and feedback reviews."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = Order.objects.get(order_id=data.get('order_id'))
            rating_val = int(data.get('rating', 5))
            review_txt = data.get('review', '').strip()

            ServiceRating.objects.update_or_create(
                order=order,
                defaults={'rating': rating_val, 'review': review_txt}
            )
            return JsonResponse({'status': 'success', 'message': 'Thank you for your rating!'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def order_receipt(request, order_id):
    """Renders printable receipt view for a given order ID."""
    order = get_object_or_404(Order, order_id=order_id)
    context = {
        'order': order,
        'hotel_phone': '+91 9175348484',
        'hotel_email': 'Hotel.shahi.swad@gmail.com',
        'hotel_address': 'Gut No. 182, Naigavhan, Tal. Phulambri, Dist. Chhatrapati Sambhajinagar',
    }
    return render(request, 'receipt.html', context)


def update_order_status_admin(request, order_id, new_status):
    """Quick status action handler for Admin Dashboard buttons."""
    if not request.user.is_staff:
        return redirect('/admin/login/')
    order = get_object_or_404(Order, order_id=order_id)
    valid_statuses = ['RECEIVED', 'PREPARING', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED']
    if new_status in valid_statuses:
        order.order_status = new_status
        if new_status == 'DELIVERED':
            order.payment_status = 'PAID'
        order.save()
    return redirect('/admin/orders/order/')


def check_new_orders_admin_api(request):
    """API that polls for new orders and triggers the audio tune & popup alert."""
    latest_order = Order.objects.order_by('-created_at').first()
    total_count = Order.objects.count()
    return JsonResponse({
        'total_count': total_count,
        'latest_id': latest_order.order_id if latest_order else None
    })


@csrf_exempt
def submit_contact_form(request):
    """Processes live contact/inquiry form submissions into database."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            mobile = data.get('mobile', '').strip()
            email = data.get('email', '').strip()
            subject = data.get('subject', 'General Inquiry').strip()
            message = data.get('message', '').strip()

            if not name or not mobile or not message:
                return JsonResponse({'status': 'error', 'message': 'Please fill in Name, Mobile Number, and Message.'})

            ContactMessage.objects.create(
                name=name,
                mobile=mobile,
                email=email,
                subject=subject,
                message=message
            )
            return JsonResponse({'status': 'success', 'message': 'Thank you! Your inquiry has been submitted. We will contact you shortly.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Server error processing request.'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def privacy_policy(request):
    """Renders Privacy Policy page for gateway compliance."""
    return render(request, 'privacy_policy.html')

def terms_conditions(request):
    """Renders Terms & Conditions page for gateway compliance."""
    return render(request, 'terms_conditions.html')

def refund_policy(request):
    """Renders Refund & Cancellation Policy page for gateway compliance."""
    return render(request, 'refund_policy.html')