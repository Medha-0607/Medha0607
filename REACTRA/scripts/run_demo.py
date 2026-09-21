"""Run all 7 deterministic RECTRA demonstration scenarios and print report."""

from __future__ import annotations

import logging
import sys

from rectra.core.logging_config import configure_logging
from rectra.demo.scenarios import run_demo_scenario

logger = logging.getLogger(__name__)


def main() -> int:
    """Execute scenarios 1 through 7 and verify pass rate."""
    configure_logging()
    print("\n" + "=" * 75)
    print("RECTRA CONTROLLED DEMONSTRATION SUITE (7 SCENARIOS)")
    print("=" * 75)

    all_passed = True

    for s_id in range(1, 8):
        res = run_demo_scenario(s_id)
        passed = res["passed"]
        all_passed = all_passed and passed

        icon = "[PASS]" if passed else "[FAIL]"
        status_tag = "PASSED" if passed else "FAILED"
        print(f"Scenario {s_id}: {res['title']}")
        print(f"   Expected: {res['expected_result']} ({res['expected_status']})")
        print(f"   Actual  : {res['actual_result']} ({res['actual_status']})")
        print(f"   Outcome : {icon} {status_tag}\n")

    print("=" * 75)
    print(f"SUMMARY: {'ALL 7 DEMO SCENARIOS PASSED!' if all_passed else 'SOME SCENARIOS FAILED!'}")
    print("=" * 75 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
