import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import process_payment, health_check


def test_process_payment():
    result = process_payment(100.0, "AUD")
    assert result["status"] == "processed"
    assert result["amount"] == 100.0
    assert result["currency"] == "AUD"
    print("  ✓ process_payment works correctly")


def test_payment_validation():
    try:
        process_payment(-10)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ rejects negative amounts")


def test_health_check():
    result = health_check()
    assert result["status"] == "healthy"
    assert result["service"] == "payment-service"
    print("  ✓ health_check returns healthy")


if __name__ == "__main__":
    print("Payment Service Tests")
    print("─────────────────────")
    passed = 0
    failed = 0
    for test_fn in [test_process_payment, test_payment_validation, test_health_check]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  ✗ {test_fn.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed > 0 else 0)
