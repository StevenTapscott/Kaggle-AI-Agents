# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from app.agent import redeem_discount, DISCOUNT_STORE

@pytest.fixture(autouse=True)
def reset_store():
    """Ensure strict test isolation by resetting in-memory store state before each test run."""
    DISCOUNT_STORE["WELCOME50"] = False
    DISCOUNT_STORE["SUMMER20"] = False
    yield
    DISCOUNT_STORE["WELCOME50"] = False
    DISCOUNT_STORE["SUMMER20"] = False

def test_discount_code_can_only_be_redeemed_once():
    """Verify a user cannot submit a request reusing a single-use code."""
    # First redemption - should succeed
    res_one = redeem_discount("WELCOME50", "user_123")
    assert "Success" in res_one
    assert DISCOUNT_STORE["WELCOME50"] is True
    
    # Second redemption trying to reuse the same code
    res_two = redeem_discount("WELCOME50", "user_456")
    assert "Error: Discount code has already been redeemed" in res_two

def test_discount_redemption_rejects_invalid_code():
    """Verify that unknown discount codes are hard-blocked."""
    res = redeem_discount("INVALID999", "user_123")
    assert "Error: Invalid discount code" in res

def test_discount_redemption_rejects_guest_accounts():
    """Verify that unauthenticated guest accounts cannot redeem discounts."""
    res = redeem_discount("SUMMER20", "guest_999")
    assert "Error: Registered user account required" in res
    assert DISCOUNT_STORE["SUMMER20"] is False
