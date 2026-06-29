import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.jd_parser import sanitise_input
from src.resume_parser import mask_pii
from src.scoring_engine import compute_weighted_total, get_recommendation

# ── Test 1: Input sanitisation ───────────────────────────────
def test_sanitise_input():
    dirty = "<script>alert('xss')</script> Senior ML Engineer"
    clean = sanitise_input(dirty)
    assert "<script>" not in clean
    assert "Senior ML Engineer" in clean
    print("✅ test_sanitise_input passed")

# ── Test 2: PII masking ──────────────────────────────────────
def test_mask_pii():
    text = "Contact me at john@example.com or +91 9876543210"
    masked = mask_pii(text)
    assert "john@example.com" not in masked
    assert "[EMAIL]" in masked
    assert "[PHONE]" in masked
    print("✅ test_mask_pii passed")

# ── Test 3: Weighted total calculation ───────────────────────
def test_compute_weighted_total():
    total = compute_weighted_total(
        skills=10,
        experience=10,
        education=10,
        projects=10,
        communication=10
    )
    assert total == 10.0
    print("✅ test_compute_weighted_total passed")

def test_compute_weighted_total_zero():
    total = compute_weighted_total(0, 0, 0, 0, 0)
    assert total == 0.0
    print("✅ test_compute_weighted_total_zero passed")

def test_compute_weighted_partial():
    total = compute_weighted_total(
        skills=8,
        experience=6,
        education=7,
        projects=5,
        communication=9
    )
    expected = round(8*0.30 + 6*0.25 + 7*0.15 + 5*0.20 + 9*0.10, 2)
    assert total == expected
    print(f"✅ test_compute_weighted_partial passed — score: {total}")

# ── Test 4: Recommendation thresholds ───────────────────────
def test_get_recommendation():
    assert get_recommendation(8.0) == "hire"
    assert get_recommendation(7.5) == "hire"
    assert get_recommendation(6.0) == "review"
    assert get_recommendation(5.0) == "review"
    assert get_recommendation(4.9) == "no-hire"
    assert get_recommendation(0.0) == "no-hire"
    print("✅ test_get_recommendation passed")

# ── Run all tests ────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🧪 Running HR Agent Tests...\n")
    test_sanitise_input()
    test_mask_pii()
    test_compute_weighted_total()
    test_compute_weighted_total_zero()
    test_compute_weighted_partial()
    test_get_recommendation()
    print("\n✅ All tests passed!\n")