# Import model classes so they register on Base.metadata for create_all()
# and for Alembic autogenerate.

from app.models.chat_upload import ChatUpload, ChatUploadChunk
from app.models.document import Chunk, Document
from app.models.exam_resource import ExamResource
from app.models.faculty import Faculty
from app.models.ingestion_log import IngestionLog
from app.models.laboratory import Laboratory
from app.models.notice import Notice
from app.models.program import Program
from app.models.push_subscription import PushSubscription
from app.models.research_project import ResearchProject
from app.models.staff import StaffMember

__all__ = [
    "ChatUpload",
    "ChatUploadChunk",
    "Document",
    "Chunk",
    "Notice",
    "ExamResource",
    "Faculty",
    "Program",
    "Laboratory",
    "PushSubscription",
    "ResearchProject",
    "StaffMember",
    "IngestionLog",
]