import pytest

from backend.economy.m2m_market import M2MMarketService


@pytest.mark.parametrize(
    ("resource", "amount", "expected"),
    [
        ("compute", 10, 0.4),
        ("energy", 10, 0.1),
        ("data", 10, 0.2),
        ("unknown", 10, 0.5),
        ("compute", 0, 0.0),
    ],
)
def test_quote_by_resource(resource: str, amount: float, expected: float):
    svc = M2MMarketService()
    assert svc.quote(resource, amount) == expected


def test_quote_rounding_precision():
    svc = M2MMarketService()
    assert svc.quote("compute", 0.3333333) == 0.013333
