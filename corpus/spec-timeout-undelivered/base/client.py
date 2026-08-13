def fetch(http, url):
    return http.get(url, timeout=5)
