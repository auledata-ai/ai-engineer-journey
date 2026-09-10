import pytest
from src import clients
from src.clients import TransientError, fetch_orders, fetch_products, fetch_users


class FlakyApi:
    def __init__(self, fail_times):
        self.fail_times, self.calls = fail_times, 0
    def get(self, path):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise TransientError(path)
        return {"path": path}


@pytest.mark.parametrize("fn,path", [(fetch_users, "/users"), (fetch_orders, "/orders"), (fetch_products, "/products")])
def test_retries_then_succeeds(fn, path):
    api = FlakyApi(fail_times=2)
    assert fn(api) == {"path": path} and api.calls == 3

def test_gives_up_after_three():
    with pytest.raises(TransientError):
        fetch_users(FlakyApi(fail_times=5))

def test_retry_decorator_exists_and_works():
    assert callable(clients.retry)
    calls = {"n": 0}
    @clients.retry(times=4, exceptions=(KeyError,))
    def flaky():
        calls["n"] += 1
        if calls["n"] < 4:
            raise KeyError("x")
        return "ok"
    assert flaky() == "ok" and calls["n"] == 4
