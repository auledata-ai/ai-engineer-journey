class TransientError(Exception):
    pass


def fetch_users(api, times: int = 3):
    last = None
    for _ in range(times):
        try:
            return api.get("/users")
        except TransientError as e:
            last = e
    raise last


def fetch_orders(api, times: int = 3):
    last = None
    for _ in range(times):
        try:
            return api.get("/orders")
        except TransientError as e:
            last = e
    raise last


def fetch_products(api, times: int = 3):
    last = None
    for _ in range(times):
        try:
            return api.get("/products")
        except TransientError as e:
            last = e
    raise last
