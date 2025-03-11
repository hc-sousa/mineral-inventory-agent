from django.shortcuts import redirect

def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    next_url = request.GET.get('next', '')
    login_url = '/accounts/login'
    if next_url:
        login_url = f"{login_url}?next={next_url}"
        
    return redirect(login_url)

def logout(request):
    return redirect('/accounts/logout')
