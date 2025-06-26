from .models import Cart

def get_or_create_cart(request):
    """
    Retrieves or creates a cart for the current session,
    handling both authenticated and anonymous users.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
        
    return cart 