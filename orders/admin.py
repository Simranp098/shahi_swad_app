import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count
from .models import (
    Category, 
    MenuItem, 
    CustomerProfile, 
    Order, 
    OrderItem, 
    OfferBanner, 
    ServiceRating,
    ContactMessage
)

# Custom Admin Dashboard Branding
admin.site.site_header = "Shahi Swad - Kitchen Dashboard"
admin.site.site_title = "Shahi Swad Admin"
admin.site.index_title = "Live Order Processing & Executive Analytics"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order']
    list_editable = ['display_order']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'food_type', 'is_available']
    list_filter = ['category', 'food_type', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_available']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['item_name', 'quantity', 'price', 'portion']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 
        'customer_name', 
        'mobile_number', 
        'total_amount', 
        'colored_order_status', 
        'quick_actions', 
        'colored_payment_status', 
        'payment_method', 
        'created_at', 
        'print_receipt_btn'
    ]
    list_filter = ()
    search_fields = ['order_id', 'customer_name', 'mobile_number', 'delivery_address']
    inlines = [OrderItemInline]
    actions = [
        'export_as_csv', 
        'mark_as_paid_cash', 
        'mark_as_paid_online', 
        'mark_as_out_for_delivery',
        'mark_as_delivered'
    ]

    def colored_order_status(self, obj):
        colors = {
            'RECEIVED': '#0284c7',         # Bright Blue
            'PREPARING': '#ea580c',        # Deep Orange
            'OUT_FOR_DELIVERY': '#9333ea', # Vibrant Purple
            'DELIVERED': '#16a34a',        # Emerald Green
            'CANCELLED': '#dc2626',        # Red
        }
        color = colors.get(obj.order_status, '#64748b')
        return format_html(
            '<span style="background-color:{}; color:white; padding:5px 12px; border-radius:20px; font-weight:700; font-size:11px; text-transform:uppercase; display:inline-block; letter-spacing:0.5px;">{}</span>',
            color, obj.get_order_status_display()
        )
    colored_order_status.short_description = "Status"

    def quick_actions(self, obj):
        if obj.order_status == 'RECEIVED':
            return format_html(
                '<a style="background:#16a34a; color:white; font-weight:800; padding:6px 14px; border-radius:20px; text-decoration:none; display:inline-block; font-size:12px; box-shadow:0 2px 6px rgba(22,163,74,0.3);" href="/api/set-order-status/{}/PREPARING/">👨‍🍳 Accept & Cook</a>',
                obj.order_id
            )
        elif obj.order_status == 'PREPARING':
            return format_html(
                '<a style="background:#9333ea; color:white; font-weight:800; padding:6px 14px; border-radius:20px; text-decoration:none; display:inline-block; font-size:12px; box-shadow:0 2px 6px rgba(147,51,234,0.3);" href="/api/set-order-status/{}/OUT_FOR_DELIVERY/">🛵 Out for Delivery</a>',
                obj.order_id
            )
        elif obj.order_status == 'OUT_FOR_DELIVERY':
            return format_html(
                '<a style="background:#0284c7; color:white; font-weight:800; padding:6px 14px; border-radius:20px; text-decoration:none; display:inline-block; font-size:12px; box-shadow:0 2px 6px rgba(2,132,199,0.3);" href="/api/set-order-status/{}/DELIVERED/">✅ Complete Order</a>',
                obj.order_id
            )
        elif obj.order_status == 'DELIVERED':
            return mark_safe('<span style="color:#16a34a; font-weight:800;">✓ Completed</span>')
        else:
            return mark_safe('<span style="color:#dc2626; font-weight:800;">Cancelled</span>')
    quick_actions.short_description = "Quick Change Status"

    def colored_payment_status(self, obj):
        color = '#16a34a' if obj.payment_status == 'PAID' else '#dc2626'
        return format_html(
            '<span style="background-color:{}; color:white; padding:4px 10px; border-radius:12px; font-weight:700; font-size:11px; text-transform:uppercase;">{}</span>',
            color, obj.get_payment_status_display()
        )
    colored_payment_status.short_description = "Payment"

    def print_receipt_btn(self, obj):
        if obj and obj.order_id:
            return format_html(
                '<a style="background:#0f172a; color:white; padding:5px 12px; border-radius:6px; font-weight:700; text-decoration:none; font-size:12px;" href="/api/orders/{}/receipt/" target="_blank">🖨️ Receipt</a>',
                obj.order_id
            )
        return ""
    print_receipt_btn.short_description = "Print"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        today = timezone.now().date()
        today_orders = Order.objects.filter(created_at__date=today)
        total_revenue = today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
        today_orders_count = today_orders.count()
        all_time_orders_count = Order.objects.count()
        total_customers = CustomerProfile.objects.count()
        total_menu_items = MenuItem.objects.filter(is_available=True).count()

        kpi_html = f"""
        <style>
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 18px; }}
            .kpi-card {{ background: #ffffff; padding: 16px 18px; border-radius: 14px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.03); color: #0f172a; }}
            .kpi-title {{ font-size: 11px; color: #64748b; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
            .kpi-value {{ font-size: 24px; font-weight: 900; color: #0f172a; margin: 4px 0; }}
            .kpi-badge {{ font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; }}
            .sound-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px 18px; border-radius: 12px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; color: #166534; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }}
        </style>

        <div class="kpi-grid">
            <div class="kpi-card" style="border-left: 5px solid #16a34a;">
                <div class="kpi-title">Today's Revenue</div>
                <div class="kpi-value">₹{total_revenue:,.2f}</div>
                <div class="kpi-badge" style="color: #16a34a;">▲ Live Sales Today</div>
            </div>
            <div class="kpi-card" style="border-left: 5px solid #0284c7;">
                <div class="kpi-title">Today's Orders</div>
                <div class="kpi-value">{today_orders_count}</div>
                <div class="kpi-badge" style="color: #0284c7;">📦 Kitchen Queue</div>
            </div>
            <div class="kpi-card" style="border-left: 5px solid #2563eb;">
                <div class="kpi-title">All-Time Orders</div>
                <div class="kpi-value">{all_time_orders_count}</div>
                <div class="kpi-badge" style="color: #2563eb;">📊 Total Received</div>
            </div>
            <div class="kpi-card" style="border-left: 5px solid #9333ea;">
                <div class="kpi-title">Total Customers</div>
                <div class="kpi-value">{total_customers}</div>
                <div class="kpi-badge" style="color: #9333ea;">👤 User Accounts</div>
            </div>
            <div class="kpi-card" style="border-left: 5px solid #ea580c;">
                <div class="kpi-title">Active Dishes</div>
                <div class="kpi-value">{total_menu_items}</div>
                <div class="kpi-badge" style="color: #ea580c;">🍛 Available Items</div>
            </div>
        </div>

        <div class="sound-box">
            <div style="font-size: 13px; font-weight: 600;">
                <span style="color: #16a34a; font-weight: 800; margin-right: 8px;">● Live Polling Active (4s)</span>
                <strong>🔊 Automatic Kitchen Chime Ready:</strong> Plays sound & displays banner instantly on every incoming order.
            </div>
            <button id="enable-sound-btn" onclick="enableAudioAlerts()" style="background: #16a34a; color: white; border: none; padding: 7px 16px; border-radius: 20px; font-weight: 800; font-size: 12px; cursor: pointer;">
                ✅ Audio Alerts Ready
            </button>
        </div>
        """

        script_html = """
        <script>
        let lastCount = null;
        let audioCtx = null;

        function enableAudioAlerts() {
            try {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') audioCtx.resume();
            } catch(e) {}
        }

        document.addEventListener('click', enableAudioAlerts, { once: true });

        function playLoudKitchenChime() {
            try {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') audioCtx.resume();

                const now = audioCtx.currentTime;
                
                const osc1 = audioCtx.createOscillator();
                const gain1 = audioCtx.createGain();
                osc1.type = 'sine';
                osc1.frequency.setValueAtTime(987.77, now);
                gain1.gain.setValueAtTime(0.8, now);
                gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.8);
                osc1.connect(gain1);
                gain1.connect(audioCtx.destination);
                osc1.start(now);
                osc1.stop(now + 0.8);

                const osc2 = audioCtx.createOscillator();
                const gain2 = audioCtx.createGain();
                osc2.type = 'sine';
                osc2.frequency.setValueAtTime(1318.51, now + 0.3);
                gain2.gain.setValueAtTime(1.0, now + 0.3);
                gain2.gain.exponentialRampToValueAtTime(0.001, now + 1.2);
                osc2.connect(gain2);
                gain2.connect(audioCtx.destination);
                osc2.start(now + 0.3);
                osc2.stop(now + 1.2);
            } catch(e) {}
        }

        function pollOrders() {
            fetch('/api/admin/check-new-orders/')
            .then(r => r.json())
            .then(data => {
                if (lastCount !== null && data.total_count > lastCount) {
                    playLoudKitchenChime();
                    
                    let popup = document.createElement('div');
                    popup.style.cssText = 'position:fixed; top:20px; right:20px; z-index:999999; background:#dc2626; color:white; padding:20px 28px; border-radius:16px; font-weight:bold; font-size:18px; box-shadow:0 20px 40px rgba(0,0,0,0.5);';
                    popup.innerHTML = '🔔 NEW ORDER RECEIVED! #' + (data.latest_id || '') + '<br><span style="font-size:14px; font-weight:normal;">Refreshing Dashboard...</span>';
                    document.body.appendChild(popup);

                    setTimeout(() => { window.location.reload(); }, 2500);
                }
                lastCount = data.total_count;
            })
            .catch(() => {});
        }

        setInterval(pollOrders, 4000);
        pollOrders();
        </script>
        """

        extra_context['title'] = mark_safe(f"{kpi_html} {script_html}")
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description='📥 Export Selected Delivery Orders to CSV / Excel')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        filename = f"shahi_swad_delivery_sales_{timezone.now().strftime('%Y_%m_%d')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer Name', 'Mobile', 'Delivery Address', 'Total Amount (₹)', 'Payment Method', 'Payment Status', 'Order Status', 'Date & Time'])

        for order in queryset:
            writer.writerow([
                order.order_id,
                order.customer_name,
                order.mobile_number,
                order.delivery_address,
                order.total_amount,
                order.get_payment_method_display(),
                order.get_payment_status_display(),
                order.get_order_status_display(),
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

    @admin.action(description='Mark selected as PAID (Cash / COD)')
    def mark_as_paid_cash(self, request, queryset):
        queryset.update(payment_status='PAID', payment_method='COD', order_status='DELIVERED')

    @admin.action(description='Mark selected as PAID (Online / UPI)')
    def mark_as_paid_online(self, request, queryset):
        queryset.update(payment_status='PAID', payment_method='UPI')

    @admin.action(description='Mark selected as OUT FOR DELIVERY')
    def mark_as_out_for_delivery(self, request, queryset):
        queryset.update(order_status='OUT_FOR_DELIVERY')

    @admin.action(description='Mark selected as DELIVERED')
    def mark_as_delivered(self, request, queryset):
        queryset.update(order_status='DELIVERED', payment_status='PAID')


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile_number', 'email', 'order_count', 'total_spent', 'created_at']
    search_fields = ['name', 'mobile_number', 'address', 'email']

    def order_count(self, obj):
        count = Order.objects.filter(mobile_number=obj.mobile_number).count()
        return format_html('<b>{} orders</b>', count)
    order_count.short_description = "Total Orders"

    def total_spent(self, obj):
        spent = Order.objects.filter(mobile_number=obj.mobile_number).aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
        return format_html('<span style="color:#16a34a; font-weight:bold;">₹{:,.2f}</span>', spent)
    total_spent.short_description = "Total Spent"


@admin.register(OfferBanner)
class OfferBannerAdmin(admin.ModelAdmin):
    list_display = ['message', 'is_active', 'created_at']
    list_editable = ['is_active']


@admin.register(ServiceRating)
class ServiceRatingAdmin(admin.ModelAdmin):
    list_display = ['order', 'rating', 'review', 'created_at']
    list_filter = ['rating']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'subject', 'created_at')
    search_fields = ('name', 'mobile', 'email', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)