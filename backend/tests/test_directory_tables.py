# API tests for the real-data directory tables with an isolated SQLite DB:
# /api/programs, /api/laboratories, /api/research-projects, /api/staff.

import pytest
import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app
from app.models.laboratory import Laboratory
from app.models.program import Program
from app.models.research_project import ResearchProject
from app.models.staff import StaffMember
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)

_seed = Session(_engine, expire_on_commit=False)
_seed.add(Program(name="M.C.A.", level="pg", intake_seats="60", source_url="https://amu.ac.in/pg"))
_seed.add(Laboratory(name="Research Lab", source_url="https://amu.ac.in/labs"))
_seed.add(ResearchProject(
    title="ERP Mission Project", status="completed",
    funding_agency="MHRD", principal_investigator="Dr. U. Bokhari",
    source_url="https://amu.ac.in/research",
))
_seed.add(StaffMember(name="Mr. A. Khan", designation="Technical Assistant",
                      source_url="https://amu.ac.in/staff"))
_seed.commit()
_seed.close()

client = TestClient(app)


def override_get_db():
    db = Session(_engine)
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _isolate_db_override():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


def test_programs_list() -> None:
    resp = client.get("/api/programs")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["id"]
    assert data[0]["name"] == "M.C.A."
    assert data[0]["level"] == "pg"


def test_programs_filter_by_level() -> None:
    resp = client.get("/api/programs?level=pg")
    assert resp.status_code == 200
    assert all(p["level"] == "pg" for p in resp.json())
    resp = client.get("/api/programs?level=phd")
    assert resp.status_code == 200
    assert resp.json() == []


def test_laboratories_list() -> None:
    resp = client.get("/api/laboratories")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Research Lab"


def test_research_projects_list_and_filter() -> None:
    resp = client.get("/api/research-projects")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["funding_agency"]
    completed = client.get("/api/research-projects?status=completed")
    assert all(p["status"] == "completed" for p in completed.json())


def test_staff_list() -> None:
    resp = client.get("/api/staff")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Mr. A. Khan"