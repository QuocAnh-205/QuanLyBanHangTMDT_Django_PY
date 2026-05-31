from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http.response import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from myshop.forms import RegistrationForm, LoginForm, ForgotPasswordForm

def register_user(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Đăng ký thành công! Hãy đăng nhập.', 'redirect': '/user/login'}, status=200)
            messages.success(request, 'Đăng ký tài khoản thành công! Vui lòng đăng nhập.')
            return redirect('login_user')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: errors[0] for field, errors in form.errors.items()}
                return JsonResponse({'errors': errors}, status=400)
    return render(
        request=request,
        template_name='user/register.html',
        context={
            'form': form
        }
    )

def login_user(request):
    form = LoginForm()
    message = ""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password']
            )
            if user:
                login(request=request, user=user)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'message': 'Đăng nhập thành công!', 'redirect': '/'}, status=200)
                if request.GET.get('next'):
                    return HttpResponseRedirect(request.GET['next'])
                return redirect('index')
            else:
                message = 'Vui lòng kiểm tra lại Username/Password'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'message': message}, status=400)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: errors[0] for field, errors in form.errors.items()}
                return JsonResponse({'errors': errors}, status=400)
                
    return render(
        request=request,
        template_name='user/login.html',
        context={
            'form': form,
            'message': message
        }
    )

def forgot_password(request):
    form = ForgotPasswordForm()
    message = ""
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'message': 'Đặt lại mật khẩu thành công! Hãy đăng nhập.', 'redirect': '/user/login'}, status=200)
                messages.success(request, 'Khôi phục mật khẩu thành công! Vui lòng đăng nhập với mật khẩu mới.')
                return redirect('login_user')
            except Exception as e:
                message = "Đã xảy ra lỗi khi đổi mật khẩu."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'message': message}, status=400)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Return standard list of validation errors
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list[0]
                if '__all__' in form.errors:
                    errors['non_field_errors'] = form.errors['__all__'][0]
                return JsonResponse({'errors': errors}, status=400)
                
    return render(
        request=request,
        template_name='user/forgot_password.html',
        context={
            'form': form,
            'message': message
        }
    )

from django.contrib.auth import logout as django_logout

def logout_user(request):
    django_logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công.')
    return redirect('index')

def validate_username(request):
    if request.method == "POST":
        username = request.POST['username']
        try:
            User.objects.get(username=username)
            return JsonResponse({'message': f'{username} đã trùng'}, status=409)
        except User.DoesNotExist:
            return JsonResponse({'message': 'OK'}, status=200)
