// Types for the directory areas: documents, research, faculty.

export interface FacultyMember {
  id: string;
  name: string;
  title: string | null;
  designation: string | null;
  department: string | null;
  email: string | null;
  phone: string | null;
  specializations: string[];
  research_areas: string[];
  profile_url: string | null;
}

export interface DocumentListItem {
  id: string;
  title: string;
  source_type: string | null;
  document_type: string | null;
  department: string | null;
  status: string;
}

export interface DocumentChunk {
  id: string;
  chunk_index: number;
  text: string;
  page_number: number | null;
}

export interface DocumentDetail extends DocumentListItem {
  source_url: string;
  publication_date: string | null;
  updated_at: string | null;
  chunks: DocumentChunk[];
}