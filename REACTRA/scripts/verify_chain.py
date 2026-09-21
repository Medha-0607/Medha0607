"""Verify the integrity of the local RECTRA evidence chain from the command line."""

from __future__ import annotations

import logging
import sys

from rectra.core.logging_config import configure_logging
from rectra.evidence.chain import verify_chain

logger = logging.getLogger(__name__)


def main() -> int:
    """Verify evidence chain and output results."""
    configure_logging()
    logger.info("Starting evidence chain integrity verification...")
    result = verify_chain()

    status_str = "INTACT (PASSED)" if result.valid else "COMPROMISED (FAILED)"
    print("\n" + "=" * 60)
    print("RECTRA EVIDENCE CHAIN INTEGRITY REPORT")
    print("=" * 60)
    print(f"Total Records Inspected : {result.total_records}")
    print(f"Chain Integrity Status  : {status_str}")
    print(f"Details                 : {result.reason}")
    if result.broken_at_test_id:
        print(f"Broken at Test ID       : {result.broken_at_test_id}")
    print("=" * 60 + "\n")

    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
