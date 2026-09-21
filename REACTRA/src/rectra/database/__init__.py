"""Database access and repository package for RECTRA."""

from rectra.database.connection import get_connection
from rectra.database.repository import (
    append_audit_chain_entry,
    get_evidence_record,
    get_test_session,
    save_evidence_record,
    save_test_session,
    search_test_history,
)
from rectra.database.schema import create_tables

__all__ = [
    "append_audit_chain_entry",
    "create_tables",
    "get_connection",
    "get_evidence_record",
    "get_test_session",
    "save_evidence_record",
    "save_test_session",
    "search_test_history",
]
