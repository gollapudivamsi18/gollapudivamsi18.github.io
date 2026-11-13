import os
import sys
import unittest
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from transaction_api import Ledger, ValidationError  # noqa: E402


def req(**overrides):
    base = {"idempotency_key": "k1", "from_account": "DEMO-ACC-001",
            "to_account": "DEMO-ACC-002", "amount": "1000.00"}
    base.update(overrides)
    return base


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()

    def test_successful_transfer(self):
        result = self.ledger.transfer(req())
        self.assertEqual(result["status"], "completed")
        self.assertEqual(self.ledger.balances["DEMO-ACC-002"], Decimal("13500.00"))

    def test_retry_is_idempotent(self):
        self.ledger.transfer(req())
        self.ledger.transfer(req())
        self.assertEqual(self.ledger.balances["DEMO-ACC-001"], Decimal("49000.00"))

    def test_rejects_insufficient_funds(self):
        with self.assertRaises(ValidationError):
            self.ledger.transfer(req(amount="60000"))

    def test_rejects_bad_amounts(self):
        for bad in ("-5", "0", "abc", "10.555", "250000"):
            with self.subTest(amount=bad), self.assertRaises(ValidationError):
                self.ledger.transfer(req(idempotency_key=bad, amount=bad))

    def test_requires_idempotency_key(self):
        with self.assertRaises(ValidationError):
            self.ledger.transfer(req(idempotency_key=""))

    def test_same_account_rejected(self):
        with self.assertRaises(ValidationError):
            self.ledger.transfer(req(to_account="DEMO-ACC-001"))


if __name__ == "__main__":
    unittest.main()
