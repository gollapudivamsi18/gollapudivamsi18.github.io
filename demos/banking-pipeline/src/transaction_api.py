"""Sample Transaction API logic for the banking pipeline demo.

Independent portfolio demo: fictional bank, synthetic accounts, no real data.
The logic is deliberately small so the focus stays on the delivery pipeline.
"""
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

MAX_TRANSFER = Decimal("200000.00")   # per-transaction limit in INR (demo value)


class ValidationError(ValueError):
    """Raised when a transfer request is invalid."""


@dataclass
class Ledger:
    balances: dict = field(default_factory=lambda: {
        "DEMO-ACC-001": Decimal("50000.00"),
        "DEMO-ACC-002": Decimal("12500.00"),
    })
    processed: dict = field(default_factory=dict)   # idempotency key -> result

    def transfer(self, request: dict) -> dict:
        key = request.get("idempotency_key")
        if not key:
            raise ValidationError("idempotency_key is required")
        if key in self.processed:            # safe retry: same answer, no double debit
            return self.processed[key]

        src, dst = request.get("from_account"), request.get("to_account")
        if src not in self.balances or dst not in self.balances:
            raise ValidationError("unknown account")
        if src == dst:
            raise ValidationError("source and destination must differ")
        try:
            amount = Decimal(str(request.get("amount")))
        except (InvalidOperation, TypeError):
            raise ValidationError("amount must be a number") from None
        if amount <= 0 or amount != amount.quantize(Decimal("0.01")):
            raise ValidationError("amount must be positive with at most 2 decimals")
        if amount > MAX_TRANSFER:
            raise ValidationError("amount exceeds per-transaction limit")
        if self.balances[src] < amount:
            raise ValidationError("insufficient funds")

        self.balances[src] -= amount
        self.balances[dst] += amount
        result = {"status": "completed", "amount": str(amount),
                  "from_balance": str(self.balances[src])}
        self.processed[key] = result
        return result
