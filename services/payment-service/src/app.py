# Payment Service

app_name = "payment-service"
version = "1.0.0"


def process_payment(amount: float, currency: str = "AUD") -> dict:
    """Process a payment transaction."""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return {
        "status": "processed",
        "amount": amount,
        "currency": currency,
        "service": app_name,
    }


def health_check() -> dict:
    return {"status": "healthy", "service": app_name, "version": version}


if __name__ == "__main__":
    print(health_check())
