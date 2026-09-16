# Import model classes so they register on Base.metadata for create_all()
# and for Alembic autogenerate.

from app.models.document import Chunk, Document
from app.models.notice import Notice

__all__ = ["Document", "Chunk", "Notice"]
