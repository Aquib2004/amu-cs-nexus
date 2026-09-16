# A small generic repository with the operations common to every model.
# Specific repositories inherit and add their own queries.

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Base class holding a session and a model type."""

    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def add(self, obj: ModelT) -> ModelT:
        """Persist a new object and return it with fresh (DB) values."""
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get(self, obj_id) -> ModelT | None:
        """Fetch a single row by primary key, or None."""
        return self.session.get(self.model, obj_id)
