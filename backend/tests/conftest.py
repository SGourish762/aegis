import os
import tempfile

import pytest

from app.audit import store as audit_store


@pytest.fixture(autouse=True, scope="session")
def _isolated_audit_db():
    """Point the audit store at a throwaway sqlite file for the whole test
    session so tests never read or write the dev aegis.db.
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    audit_store.init_db(f"sqlite:///{path}")
    yield
    os.remove(path)
