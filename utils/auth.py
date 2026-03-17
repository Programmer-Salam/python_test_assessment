from functools import wraps

def internal_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow the request to pass through
        return f(*args, **kwargs)
    return decorated_function
