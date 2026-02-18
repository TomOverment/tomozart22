# store/context_processors.py

CART_SESSION_KEY = "cart"

def cart_count(request):
    """
    Makes `cart_count` available in every template.
    Session cart format: { "12": 2, "9": 1 }
    """
    cart = request.session.get(CART_SESSION_KEY, {}) or {}
    try:
        count = sum(int(q) for q in cart.values())
    except (TypeError, ValueError):
        count = 0
    return {"cart_count": count}
