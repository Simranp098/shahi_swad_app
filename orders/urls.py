from django.urls import path
from . import views

urlpatterns = [
    # Customer Web App Main Page
    path('', views.customer_menu, name='customer_menu'),

    # Auth & Account Management APIs
    path('api/check-mobile/', views.check_mobile_api, name='check_mobile_api'),
    path('api/register-pin/', views.register_pin_api, name='register_pin_api'),
    path('api/login-pin/', views.login_pin_api, name='login_pin_api'),
    path('api/logout/', views.logout_api, name='logout_api'),
    path('api/update-profile/', views.update_profile_api, name='update_profile_api'),

    # Forgot Password / PIN OTP Verification APIs
    path('api/request-pin-reset/', views.request_pin_reset_api, name='request_pin_reset_api'),
    path('api/verify-reset-pin/', views.verify_and_reset_pin_api, name='verify_and_reset_pin_api'),

    # Order Processing & History APIs
    path('api/place-order/', views.place_order_api, name='place_order_api'),
    path('api/active-orders/', views.active_orders_api, name='active_orders_api'),
    path('api/order-history/', views.get_order_history_api, name='get_order_history_api'),
    path('api/submit-rating/', views.submit_rating_api, name='submit_rating_api'),
    path('api/orders/<str:order_id>/receipt/', views.order_receipt, name='order_receipt'),

    # PhonePe Payment Gateway Callbacks
    path('payments/phonepe/response/', views.phonepe_response, name='phonepe_response'),
    path('payments/phonepe/webhook/', views.phonepe_webhook, name='phonepe_webhook'),

    # Admin Dashboard Live Polling & Action APIs
    path('api/set-order-status/<str:order_id>/<str:new_status>/', views.update_order_status_admin, name='update_order_status_admin'),
    path('api/admin/check-new-orders/', views.check_new_orders_admin_api, name='check_new_orders_admin_api'),

    # Contact & Inquiry Form API
    path('api/submit-contact/', views.submit_contact_form, name='submit_contact_form'),
    # Mandatory Compliance Pages for Gateway Approval
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('refund-and-cancellation/', views.refund_policy, name='refund_policy'),
]