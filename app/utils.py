import bleach


def xss_clean(user_input):
    """Utility to prevent XSS attacks and sanitize user input."""
    return bleach.clean(user_input)
