from urllib.parse import urlparse

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    


def get_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None