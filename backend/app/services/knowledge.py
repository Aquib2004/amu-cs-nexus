"""Structured AMU knowledge merged with the semantic document corpus."""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exam_resource import ExamResource
from app.models.faculty import Faculty
from app.models.laboratory import Laboratory
from app.models.notice import Notice
from app.models.program import Program
from app.models.research_project import ResearchProject
from app.models.staff import StaffMember
from app.services.search import search_chunks

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOP = {
    "a", "an", "and", "are", "as", "at", "about", "by", "can", "check", "do",
    "does", "for", "from", "how", "i", "in", "is", "of", "on", "or", "tell",
    "the", "to", "what", "when", "where", "which", "who", "with",
}

# Explicit domain words outrank incidental text overlap. For example, a long
# programme outcome document may contain "student" and "result", but a question
# about checking a result must retrieve exam resources first.
_DOMAIN_WORDS = {
    "exam": {"exam", "examination", "examinations", "result", "results", "marksheet", "transcript", "reevaluation"},
    "notice": {"notice", "notices", "circular", "announcement", "latest", "recent", "newest"},
    "faculty": {"faculty", "professor", "chairperson", "head", "hod", "teacher"},
    "programme": {"programme", "program", "programmes", "course", "courses", "mca", "msc", "bsc", "phd", "eligibility", "intake", "syllabus"},
    "laboratory": {"lab", "labs", "laboratory", "laboratories", "facility", "facilities"},
    "research": {"research", "project", "projects", "publication", "publications", "funded"},
    "staff": {"staff", "nonteaching", "technical", "administrative", "office"},
}


def _domains(query: str) -> set[str]:
    words = set(_TOKEN_RE.findall(query.lower()))
    return {domain for domain, markers in _DOMAIN_WORDS.items() if words & markers}


def _broad_list_question(query: str) -> bool:
    words = set(_TOKEN_RE.findall(query.lower()))
    return bool(words & {"what", "which", "list", "available", "show", "departments", "laboratories", "labs", "projects", "staff", "programmes", "courses"})


@dataclass
class KnowledgeHit:
    chunk_id: UUID
    document_id: UUID
    text: str
    source_url: str
    score: float
    title: str
    source_type: str = "official"


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if t not in _STOP}


def _joined(*values) -> str:
    return " · ".join(str(v).strip() for v in values if v is not None and str(v).strip())


def _score(query: str, text: str, name: str | None = None) -> float:
    query_tokens = set(_TOKEN_RE.findall(query.lower()))
    text_tokens = _tokens(text)
    if not query_tokens or not text_tokens:
        return 0.0
    score = len(query_tokens & text_tokens) / len(query_tokens)
    phrase = query.lower().strip(" ?.!")
    if name:
        normalized = re.sub(r"^(prof|dr|mr|ms|mrs)\.?\s+", "", name.lower()).strip()
        parts = [part for part in normalized.split() if len(part) > 2]
        if normalized and normalized in phrase:
            score += 2.5
        elif len(parts) > 1:
            similarity = max(SequenceMatcher(None, part, phrase).ratio() for part in parts)
            if similarity >= 0.78:
                score += 2.2
            elif sum(part in phrase for part in parts) >= max(1, len(parts) - 1):
                score += 1.5
    return score


def _as_hit(row, text: str, source_url: str, source_type: str, query: str):
    score = _score(query, text, getattr(row, "name", None))
    if score <= 0:
        return None
    return KnowledgeHit(
        chunk_id=row.id,
        document_id=row.id,
        text=text,
        source_url=source_url,
        score=score,
        title=getattr(row, "name", None) or getattr(row, "title", None) or "Official resource",
        source_type=source_type,
    )


def _format_faculty(row: Faculty) -> str:
    return _joined(
        f"Faculty member: {row.name}",
        f"Designation: {row.designation}" if row.designation else None,
        f"Email: {row.email}" if row.email else None,
        f"Phone: {row.phone}" if row.phone else None,
        "Specializations: " + ", ".join(row.specializations or []) if row.specializations else None,
        "Research areas: " + ", ".join(row.research_areas or []) if row.research_areas else None,
        f"Profile: {row.profile_url}" if row.profile_url else None,
    )


def _format_staff(row: StaffMember) -> str:
    return _joined(
        f"Non-teaching staff member: {row.name}", f"Designation: {row.designation}",
        f"Email: {row.email}" if row.email else None, f"Phone: {row.phone}" if row.phone else None,
    )


def _format_program(row: Program) -> str:
    return _joined(
        f"Programme: {row.name}", f"Level: {row.level.upper()}" if row.level else None,
        f"Intake: {row.intake_seats}" if row.intake_seats else None,
        f"Duration: {row.duration}" if row.duration else None,
        f"Eligibility: {row.eligibility}" if row.eligibility else None, row.details,
    )


def _format_lab(row: Laboratory) -> str:
    return _joined(f"Laboratory: {row.name}", row.description)


def _format_research(row: ResearchProject) -> str:
    return _joined(
        f"Research project: {row.title}", f"Status: {row.status}" if row.status else None,
        f"Funding agency: {row.funding_agency}" if row.funding_agency else None,
        f"Amount: {row.amount}" if row.amount else None,
        f"Principal investigator: {row.principal_investigator}" if row.principal_investigator else None,
        f"Co-investigators: {row.co_investigators}" if row.co_investigators else None, row.description,
    )


def _format_notice(row: Notice) -> str:
    date = row.published_at.isoformat() if row.published_at else "date not stated"
    return _joined(f"Official notice: {row.title}", f"Category: {row.category}" if row.category else None, f"Published: {date}", row.body)



def _format_exam(row: ExamResource) -> str:
    return _joined(
        f"Examination resource: {row.title}", f"Category: {row.category}",
        row.description,
    )


def search_structured(session: Session, query: str, limit: int = 12) -> list[KnowledgeHit]:
    """Search normalized official tables without relying on derived documents."""
    hits: list[KnowledgeHit] = []
    domains = _domains(query)
    broad = _broad_list_question(query)
    models = [
        (Faculty, _format_faculty, lambda r: r.profile_url or r.source_url, "faculty"),
        (StaffMember, _format_staff, lambda r: r.source_url, "staff"),
        (Program, _format_program, lambda r: r.source_url, "programme"),
        (Laboratory, _format_lab, lambda r: r.source_url, "laboratory"),
        (ResearchProject, _format_research, lambda r: r.source_url, "research"),
        (Notice, _format_notice, lambda r: r.url, "notice"),
        (ExamResource, _format_exam, lambda r: r.url, "exam"),
    ]
    for model, formatter, url_for, source_type in models:
        stmt = select(model)
        if model is Notice:
            stmt = stmt.order_by(Notice.published_at.desc().nulls_last())
        for row in session.scalars(stmt):
            text = formatter(row)
            hit = _as_hit(row, text, url_for(row), source_type, query)
            if hit is None and model is Notice and any(
                word in query.lower() for word in ("latest", "recent", "newest", "new notice")
            ):
                hit = KnowledgeHit(
                    chunk_id=row.id,
                    document_id=row.id,
                    text=text,
                    source_url=url_for(row),
                    score=0.5,
                    title=row.title,
                    source_type=source_type,
                )
            if hit is None and source_type in domains and broad:
                hit = KnowledgeHit(
                    chunk_id=row.id,
                    document_id=row.id,
                    text=text,
                    source_url=url_for(row),
                    score=2.0,
                    title=getattr(row, "name", None) or getattr(row, "title", None) or "Official resource",
                    source_type=source_type,
                )
            if hit:
                if source_type in domains:
                    hit.score += 2.0
                elif domains:
                    hit.score -= 0.5
                hits.append(hit)
    domain_hits = [hit for hit in hits if hit.source_type in domains]
    if domains and domain_hits:
        hits = domain_hits
    hits.sort(key=lambda hit: hit.score, reverse=True)
    return hits[:limit]


def search_knowledge(session: Session, query: str, limit: int = 8) -> list[KnowledgeHit]:
    """Merge structured exact-field evidence with semantic document chunks."""
    structured = search_structured(session, query, limit=max(limit, 12))
    # Exact person/name and broad official-list matches are stronger than adding
    # noisy semantic neighbors. This also avoids a needless embedding API call.
    if structured and structured[0].score >= 1.5:
        return structured[:limit]
    corpus = search_chunks(session, query=query, limit=max(limit * 3, 20))
    merged: list[KnowledgeHit] = []
    seen_urls: set[str] = set()
    for hit in structured:
        if hit.source_url not in seen_urls:
            merged.append(hit)
            seen_urls.add(hit.source_url)
    for rank, result in enumerate(corpus):
        if result.source_url in seen_urls:
            continue
        merged.append(KnowledgeHit(
            chunk_id=result.chunk_id,
            document_id=result.document_id,
            text=result.text,
            source_url=result.source_url,
            score=1.0 - rank / max(len(corpus) + 1, 1),
            title="Indexed AMU document",
            source_type="document",
        ))
        seen_urls.add(result.source_url)
    return merged[:limit]
