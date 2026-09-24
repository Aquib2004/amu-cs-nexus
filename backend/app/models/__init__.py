# Import model classes so they register on Base.metadata for create_all()
# and for Alembic autogenerate.

from app.models.document import Chunk, Document
from app.models.faculty import Faculty
from app.models.ingestion_log import IngestionLog
from app.models.laboratory import Laboratory
from app.models.notice import Notice
from app.models.program import Program
from app.models.research_project import ResearchProject
from app.models.staff import StaffMember

__all__ = [
    "Document",
    "Chunk",
    "Notice",
    "Faculty",
    "Program",
    "Laboratory",
    "ResearchProject",
    "StaffMember",
    "IngestionLog",
]