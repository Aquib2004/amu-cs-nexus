# Portable vector column type.
# pgvector.vector on PostgreSQL; CSV text on SQLite so tests run offline.

from sqlalchemy import String, TypeDecorator


class VectorType(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, dimensions: int = 384) -> None:
        super().__init__()
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(self.dimensions))
        return dialect.type_descriptor(String(8192))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return ",".join(str(float(v)) for v in value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return [float(v) for v in value.split(",")]
