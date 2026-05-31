from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.http.response import JsonResponse
from django.db.models import Min, Max
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.contrib.humanize.templatetags.humanize import intcomma
from .forms import ReviewForm
from .models import Product, Review

from myshop.models import Category, Brand, Product, Order, OrderDetail, Promotion
from myshop.templatetags.custom_filter import get_price_sale, get_price
# Create your views here.


def index(request): # View all product
    categories = Category.objects.filter(category_parent__isnull=True)
    products = Product.objects.all()
    
    # Tính toán khoảng giá thấp nhất và cao nhất trên hệ thống
    min_price_agg = products.aggregate(Min('price'))['price__min'] or 0
    max_price_agg = products.aggregate(Max('price'))['price__max'] or 0

    # Lấy các tham số lọc giá từ request
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    # Nếu là yêu cầu AJAX thì chỉ trả về phần danh sách sản phẩm đã được lọc
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            template_name='product/product_list_partial.html',
            context={'products': products, 'user': request.user},
            request=request
        )
        return JsonResponse({'html': html})

    products_promotion = Promotion.objects.filter(
            start_date__lte=now(),# ngày bắt dầu kmai < ngày hiện tại (trước ngày hiện tại)
            end_date__gt=now() # ngày kết thúc kmai > ngày hiện tại
            )
    return render(
        request=request,
        template_name='index.html',
        context={
            'categories': categories,
            'products': products,
            'minimum_price': min_price_agg,
            'maximum_price': max_price_agg,
            'products_promotion': products_promotion,
        }
    )


def brands(request, category_name): # View list product of a brand

    categories = Category.objects.filter(category_parent__isnull=True)
    brands = Category.objects.get(name=category_name).brand_set.all()
    brand_display = ''
    products = Product.objects.all()
    brand_search = request.GET.get('brand')
    category = Category.objects.get(name=category_name)
    products = Product.objects.filter(category=category)
    if brand_search:
        brand_display = Category.objects.get(name=category_name).brand_set.get(name=brand_search)
        products = products.filter(brand=brand_display)
    return render(
        request=request,
        template_name='common/brands.html',
        context={
            'brands': brands,
            'products': products,
            'category': category,
            'brand_display': brand_display,
            'categories': categories,
        }
    )


def view_product(request, product_id): # View detail product when user click
    try:
        product_data = Product.objects.get(id=product_id)
        reviews = product_data.reviews.select_related('user').order_by('-created_at')
        
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return redirect(f'/user/login?next=/product/{product_id}')
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product_data
                review.user = request.user
                review.save()
                return redirect('view_product', product_id=product_id)
        else:
            form = ReviewForm()

        product_detail = product_data.detail
        fields_data = product_detail._meta.get_fields()
        fields = []
        for field in fields_data:
            if field.name == 'product' or field.name == 'id' or field.name == 'name':
                continue
            else:
                fields.append(field.name)
        info = f'Cấu hình chi tiết của {product_data}'
        return render(
            request=request,
            template_name='product/product-details.html',
            context={
                'info': info,
                'product_data': product_data,
                'fields': fields,
                'product_detail': product_detail,
                'reviews': reviews,
                'review_form': form,
            }             
        )
    except Product.DoesNotExist:
        return render(
            request=request,
            template_name='404.html',     
        )

def product_detail_api(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        detail = product.detail
        
        # Get labels and values for specifications
        specs = []
        fields_data = detail._meta.get_fields()
        for field in fields_data:
            if field.name in ['product', 'id', 'name']:
                continue
            val = getattr(detail, field.name, '')
            label = field.verbose_name or field.name
            specs.append({
                'label': label,
                'value': val
            })

        data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'stock_quantity': product.stock_quantity,
            'image': product.image,
            'category': product.category.name,
            'brand': product.brand.name,
            'status': product.status,
            'specs': specs
        }
        return JsonResponse(data, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)



@login_required(login_url='/user/login')
def add_product_to_cart(request, product_id): # Add a produc to user's cart
    try:
        # Xác định người dùng đăng nhập
        logged_user = request.user
        product_data = Product.objects.get(id=product_id)
        # Kiểm tra xem người dùng có giỏ hàng nào chưa thành công (Status = 0)
        user_has_ordered = Order.objects.get(user=logged_user, status=0) # Status = 0 là chưa thành công
        # Người dùng có 1 order chưa thành công.
        # Chia ra làm 2 trường hợp.
        
        # Người dùng thêm trùng với sản phẩm đã có trong giỏ hàng. Cập nhật dòng Orderdetail với sản phẩm đó và tăng quantity lên 1.
        order = user_has_ordered # Đổi tên lại cho dễ xử lý
        orderdetail = OrderDetail.objects.get(order=order, product=product_data)
        # orderdetail = order.orderdetail_set.get(product=product_data)
        # Qua dòng này thì đồng nghĩa sản phẩm thêm mới trùng với 1 trong các sản phẩm trong giỏ hàng.
        # Tăng quantity += 1
        if product_data.stock_quantity > orderdetail.quantity:
            orderdetail.quantity += 1
            orderdetail.amount = orderdetail.quantity * get_price(product_data.id)
            orderdetail.save()

    except Product.DoesNotExist: # Bỏ qua
        pass

    except Order.DoesNotExist:
        if product_data.stock_quantity >= 1:
            # Rơi vào except này thì người dùng không có đơn hàng chưa thành công. (Không có gì hoặc có đơn hàng thanh toán rồi Status = 1)
            # Tạo mới 1 order vói logged_user
            new_order = Order.objects.create(
                create_date=now(),
                total_amount=0,
                phone="",
                address="",
                status=0,
                user=logged_user,
            )
            # Order không có thông tin về sản phẩm nên tạo tiếp 1 Orderdetail
            OrderDetail.objects.create(
                product=product_data,
                order=new_order,
                quantity=1,
                amount=get_price(product_data.id),
            )

    except OrderDetail.DoesNotExist:
        if product_data.stock_quantity >= 1:
            # Người dùng thêm 1 sản phẩm không trùng với cái có trong giỏ hàng. Thêm mới 1 dòng Orderdetail với sản phẩm mới.
            OrderDetail.objects.create(
                product=product_data,
                order=order,
                quantity=1,
                amount=get_price(product_data.id)
            )
    user_ordered = Order.objects.get(user=logged_user, status=0)
    quantity = sum([item.quantity for item in user_ordered.orderdetail_set.all()])
    return JsonResponse(data={'quantity': quantity})


# 2 hàm view để tăng hoặc giảm
# def increase_quantity
# def decrease_quantity

# Viết 1 hàm hỗ trợ cả tăng hoặc giảm sản phẩm, 1 hàm có tới 2 tham số
@login_required(login_url='/user/login')
def change_product_quantity(request, action, product_id):
    # action: increase/decrease
    logged_user = request.user
    product_data = Product.objects.get(id=product_id)
    order = Order.objects.get(user=logged_user, status=0)
    orderdetail = OrderDetail.objects.get(order=order, product=product_data)
    if action == 'increase':
        if product_data.stock_quantity > orderdetail.quantity:
            orderdetail.quantity += 1
            orderdetail.amount = orderdetail.quantity * get_price(product_data.id)
            orderdetail.save()
    else:
        # decrease
        # Giảm tới quantity = 1, bấm thêm 1 lần nữa thì đồng nghĩa với xoá giỏ hàng
        if orderdetail.quantity == 1:
            orderdetail.delete()
        else:
            orderdetail.quantity -= 1
            orderdetail.amount = orderdetail.quantity * get_price(product_data.id)
            orderdetail.save()

    return redirect('show_cart')


@login_required(login_url='/user/login')
def delete_product_in_cart(request, product_id):
    logged_user = request.user   
    product_data = Product.objects.get(id=product_id)
    order = Order.objects.get(user=logged_user, status=0)
    orderdetail = OrderDetail.objects.get(order=order, product=product_data)
    orderdetail.delete()
    return redirect('show_cart')


@login_required(login_url='/user/login')
def show_cart(request):
    orderdetail=[]
    message=''
    total_amount=0
    try:
        logged_user = request.user
        order = Order.objects.get(user=logged_user, status=0)
        orderdetail = order.orderdetail_set.all()
        if len(orderdetail) == 0:
            message = 'Chưa có sản phẩm nào trong giỏ hàng!!'
        else:
            total_amount = sum([item.amount for item in orderdetail])
    except:
        message = 'Chưa có sản phẩm nào trong giỏ hàng!!'
    
    return render(
        request=request,
        template_name='cart/cart.html',
        context={
            'data_orderdetail': orderdetail,
            'message': message,
            'total_amount': total_amount,
        }
    )

@login_required(login_url='/user/login')
def checkout(request):
    orderdetail = []
    logged_user = request.user
    try:
        order = Order.objects.get(user=logged_user, status=0)
        orderdetail = order.orderdetail_set.all()
    except Order.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Không tìm thấy giỏ hàng hoạt động.'}, status=400)
        return redirect('show_cart')

    total_amount = sum([item.amount for item in orderdetail])

    if request.method == "POST":
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        fullname = request.POST.get('fullname', '')
        payment_method = request.POST.get('payment_method', 'COD')
        notes = request.POST.get('notes', '')

        # Save shipping details consolidated in standard fields
        order.phone = phone
        order.address = f"Họ tên: {fullname} | Địa chỉ: {address} | HTTT: {payment_method} | Ghi chú: {notes}"
        order.total_amount = total_amount
        order.status = 1  # Đơn hàng thành công
        order.save()

        # Cập nhật số lượng tồn kho của sản phẩm
        for od_detail in orderdetail:
            od_detail.product.stock_quantity -= od_detail.quantity
            od_detail.product.save()

        # Gửi email xác nhận mua hàng (fail_silently=True để tránh crash hệ thống nếu SMTP không cấu hình đúng)
        try:
            from_email = settings.EMAIL_HOST_USER
            subject = 'Xác nhận đơn hàng thành công từ MyShop'
            message = f'''
            Xin chào {fullname or logged_user.username},
            Cảm ơn bạn đã mua sắm tại MyShop! Đơn hàng của bạn đã được thanh toán và xử lý thành công.

            Chi tiết đơn hàng:
            - Mã đơn hàng: DH{order.id}
            - Tổng giá trị thanh toán: {intcomma(total_amount)} VND
            - Phương thức thanh toán: {payment_method}
            - Số điện thoại nhận hàng: {phone}
            - Địa chỉ giao hàng: {address}

            Đơn hàng sẽ nhanh chóng được chuẩn bị và bàn giao cho đơn vị vận chuyển.
            Chúc bạn một ngày tốt lành!

            Trân trọng,
            Đội ngũ MyShop
            '''
            recipient_list = [logged_user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
        except Exception as e:
            print("Mail sending error:", e)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Đơn hàng đã được thanh toán thành công!',
                'redirect': '/',
                'order_id': order.id,
                'total_amount': total_amount
            }, status=200)
            
        return redirect('index')

    # Tạo đường dẫn VietQR để quét thanh toán động
    bank_id = "MB"
    account_no = "123456789"
    account_name = "NGUYEN QUOC ANH"
    qr_url = f"https://img.vietqr.io/image/{bank_id}-{account_no}-compact2.png?amount={total_amount}&addInfo=DH{order.id}&accountName={account_name.replace(' ', '%20')}"

    return render(
        request=request,
        template_name='cart/checkout.html',
        context={
            'data_orderdetail': orderdetail,
            'total_amount': total_amount,
            'qr_url': qr_url,
            'bank_name': 'Ngân hàng Quân Đội (MB Bank)',
            'account_no': account_no,
            'account_name': account_name,
            'order_code': f"DH{order.id}"
        }
    )

def user_logout(request):
    logout(request)
    return redirect('login')

def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)
    reviews = product.reviews.select_related('user').order_by('-created_at')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'product_detail.html', {
        'product_data': product,
        'reviews': reviews,
        'review_form': form,
    })