// Types for the directory areas: documents, research, faculty, programmes.

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
  image_url: string | null;
  source_url: string;
}

export interface ProgramRead {
  id: string;
  name: string;
  level: string | null;
  intake_seats: string | null;
  duration: string | null;
  eligibility: string | null;
  curriculum_url: string | null;
  syllabus_url: string | null;
  details: string | null;
  source_url: string;
}

export interface LaboratoryRead {
  id: string;
  name: string;
  description: string | null;
  file: string | null;
  source_url: string;
}

export interface ResearchProjectRead {
  id: string;
  title: string;
  status: string | null;
  funding_agency: string | null;
  amount: string | null;
  principal_investigator: string | null;
  co_investigators: string | null;
  description: string | null;
  source_url: string;
}

export interface StaffRead {
  id: string;
  name: string;
  designation: string | null;
  email: string | null;
  phone: string | null;
  image_url: string | null;
  profile_url: string | null;
}

export interface DocumentListItem {
  id: string;
  title: string;
  source_type: string | null;
  document_type: string | null;
  department: string | null;
  status: string;
  source_url: string | null;
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