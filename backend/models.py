"""
StudyAI Database Models
=======================

SQLAlchemy ORM models for the StudyAI system.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from database import Base

class Document(Base):
    """
    Document model representing uploaded files.

    Stores metadata about uploaded documents including filename,
    content hash for caching, and creation timestamp.
    """
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)  # MD5 hash
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationship to generated content
    generated_contents: Mapped[list["GeneratedContent"]] = relationship("GeneratedContent", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', hash='{self.content_hash[:8]}...')>"

class GeneratedContent(Base):
    """
    GeneratedContent model representing AI-generated study materials.

    Stores the AI-generated content (MCQs, theory questions, flashcards, summary)
    linked to a specific document.
    """
    __tablename__ = "generated_contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"), nullable=False, index=True)

    # JSON fields for storing arrays of content
    mcq: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # List of multiple choice questions
    theory: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # List of theory questions
    flashcards: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # List of flashcards (term-definition pairs)

    # Text field for summary
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Relationship to document
    document: Mapped["Document"] = relationship("Document", back_populates="generated_contents")

    def __repr__(self):
        return f"<GeneratedContent(id={self.id}, document_id={self.document_id}, mcq_count={len(self.mcq)})>"


# Database configuration moved to database.py
# Use database.py for database operations