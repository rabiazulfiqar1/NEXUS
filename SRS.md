# Software Requirements Specification
for
NEXUS: Agentic Career Intelligence Runtime
Version 1.0 approved
Prepared by Batool Kazmi 23K-0672, Rabia Zulfiqar 23K-0851
FAST National University
April 29th, 2026

## Table of Contents
- Table of Contents
- Revision History
1. Introduction
   1.1 Purpose
   1.2 Document Conventions
   1.3 Intended Audience and Reading Suggestions
   1.4 Product Scope
   1.5 References
2. Overall Description
   2.1 Product Perspective
   2.2 Product Functions
   2.3 User Classes and Characteristics
   2.4 Operating Environment
   2.5 Design and Implementation Constraints
   2.6 User Documentation
   2.7 Assumptions and Dependencies
3. External Interface Requirements
   3.1 User Interfaces
   3.2 Hardware Interfaces
   3.3 Software Interfaces
   3.4 Communications Interfaces
4. System Features
   4.1 Resume Upload and Parsing
   4.2 Profile Management and Embeddings
   4.3 Career Analysis and ATS Scoring
   4.4 Resume Enhancement and CV Generation
   4.5 Job Matching and Tracking
5. Other Nonfunctional Requirements
   5.1 Performance Requirements
   5.2 Safety Requirements
   5.3 Security Requirements
   5.4 Software Quality Attributes
   5.5 Business Rules
6. Other Requirements
Appendix A: Glossary
Appendix B: Analysis Models
Appendix C: To Be Determined List

## Revision History
| Name | Date | Reason For Changes | Version |
| --- | --- | --- | --- |
| Batool Kazmi, Rabia Zulfiqar | April 2026 | Initial draft | 1.0 |

---

# 1. Introduction

## 1.1 Purpose
This Software Requirements Specification (SRS) defines the requirements for NEXUS: Agentic Career Intelligence Runtime, version 1.0. The document specifies functional and nonfunctional requirements for the end-to-end system, including the backend APIs, data services, and the frontend user experience. It covers the scope of the product as delivered in this release and provides a baseline for validation and future development.

## 1.2 Document Conventions
- Requirements use the format "REQ-<number>" and are stated with "shall" to indicate mandatory behavior.
- Priority is marked as High, Medium, or Low for each feature.
- Error responses are described in terms of user-visible messaging and system-level status codes.
- Data fields and API endpoints are written in monospace for clarity.

## 1.3 Intended Audience and Reading Suggestions
- Product Owners and Stakeholders: Read Sections 1 and 2 for product scope and high-level functions.
- Developers and Architects: Read Sections 3 and 4 for interfaces and functional requirements.
- QA and Test Engineers: Read Sections 4 and 5 for testable requirements and quality attributes.
- Operations and DevOps: Read Sections 2.4, 2.5, 3, and 5 for deployment and runtime constraints.

## 1.4 Product Scope
NEXUS is a web-based career intelligence platform that helps users analyze career fit, improve resumes, and match with relevant jobs. It integrates profile parsing, embeddings, ATS scoring, market trend analysis, and AI-driven resume and CV output. The system aims to reduce time-to-insight for job seekers by automating analysis and generating actionable guidance.

## 1.5 References
- IEEE 830-1998 Recommended Practice for Software Requirements Specifications.
- FAST National University SRS formatting guidelines (internal academic reference).
- Supabase documentation for database and auth services.
- FastAPI documentation for backend API development.

---

# 2. Overall Description

## 2.1 Product Perspective
NEXUS is a standalone web application with a modular architecture consisting of:
- Frontend UI (React + Vite) for user interaction.
- Backend API (FastAPI) for business logic and orchestration.
- Data services (Supabase Postgres + Storage + RPC functions) for persistence.
- AI services (LLM provider and embedding generation) for analysis and content generation.
- Redis caching for repeated career analysis results.

The system is designed as a single product, but integrates third-party services for embeddings, LLMs, and search.

## 2.2 Product Functions
- Accept user resume uploads (PDF) and extract text.
- Maintain a structured user profile (skills, education, experience, projects).
- Generate embeddings for user profiles and jobs for similarity matching.
- Compute ATS scores for matched job listings.
- Perform career analysis to identify strengths, gaps, and trends.
- Generate enhanced resume bullet points and CV content.
- Display matched jobs and track job application status.

## 2.3 User Classes and Characteristics
- Job Seekers (Primary): Users seeking personalized career insights, resume improvement, and job matching.
- Power Users: Users who frequently adjust profile data to refine recommendations.
- Admin/Operators (Internal): Manage infrastructure, logs, and environment configuration.

## 2.4 Operating Environment
- Client: Modern web browsers (Chrome, Edge, Firefox, Safari) on desktop and mobile.
- Server: Linux-based or Windows-based deployment environment capable of running Python 3.12+.
- Backend Dependencies: FastAPI, Supabase client, Redis.
- Frontend Dependencies: Node.js 18+, Vite, React, Tailwind/standard CSS.

## 2.5 Design and Implementation Constraints
- Must use Supabase for primary data storage and auth.
- Must use FastAPI for backend endpoints and routing.
- Must support Redis caching for career analysis performance.
- Must support PDF resume parsing through a Python PDF library.
- Must use an external LLM provider (OpenRouter/Groq/Ollama) with configurable API keys.

## 2.6 User Documentation
- Quick start setup guide for developers (SETUP.md).
- Inline UI tooltips and error messaging.
- Optional developer README for deployment/configuration.

## 2.7 Assumptions and Dependencies
- Users have valid authentication sessions via Supabase.
- External APIs (LLM providers, Tavily search) are available and within rate limits.
- Redis is running and accessible for caching.
- Supabase RPC functions for similarity search are configured.

---

# 3. External Interface Requirements

## 3.1 User Interfaces
- Web UI with tabs for resume enhancement, CV generation, career analysis, job matching, and job tracking.
- File upload control for PDF resumes.
- Career analysis loading view showing multi-step agent progress.
- Results view for enhanced resume and generated CV content.

## 3.2 Hardware Interfaces
- No specialized hardware interfaces are required.
- System must operate on standard client hardware and server hardware.

## 3.3 Software Interfaces
- Supabase Postgres database for storage and RPC-based similarity search.
- Supabase Auth for user identification and secure API access.
- Redis for caching career analysis results and async job tracking.
- LLM provider for resume enhancement and CV generation.
- Embedding generator for semantic matching.

## 3.4 Communications Interfaces
- REST APIs over HTTPS for all client-server interactions.
- JSON payloads for requests and responses.
- Multipart form-data for PDF uploads.

---

# 4. System Features

## 4.1 Resume Upload and Parsing
### 4.1.1 Description and Priority
Allows users to upload a PDF resume and store extracted text. Priority: High.

### 4.1.2 Stimulus/Response Sequences
1. User selects a PDF resume.
2. Client submits upload to `/profile/resume`.
3. Server extracts text and stores it in `user_profiles.resume_text`.
4. System acknowledges completion.

### 4.1.3 Functional Requirements
- REQ-1: The system shall accept PDF uploads and reject unsupported file types.
- REQ-2: The system shall extract text from the uploaded PDF.
- REQ-3: The system shall store extracted resume text in the user profile.
- REQ-4: The system shall allow users to remove stored resume text.

## 4.2 Profile Management and Embeddings
### 4.2.1 Description and Priority
Maintains structured profile fields and generates embeddings for matching. Priority: High.

### 4.2.2 Stimulus/Response Sequences
1. User edits profile data.
2. Client sends profile data to `/profile/manual`.
3. Server stores profile and updates embeddings.

### 4.2.3 Functional Requirements
- REQ-5: The system shall store user profile fields (skills, education, experience, projects).
- REQ-6: The system shall generate and store embeddings from profile data or resume text.
- REQ-7: The system shall allow profile updates without requiring resume re-upload.

## 4.3 Career Analysis and ATS Scoring
### 4.3.1 Description and Priority
Performs career analysis by matching jobs and computing ATS score. Priority: High.

### 4.3.2 Stimulus/Response Sequences
1. User requests career analysis.
2. Server computes job similarity and ATS score.
3. Server returns strengths, gaps, and ATS metrics.

### 4.3.3 Functional Requirements
- REQ-8: The system shall retrieve matched jobs using user embeddings.
- REQ-9: The system shall compute ATS score for the top matched job.
- REQ-10: The system shall return a structured analysis response.

## 4.4 Resume Enhancement and CV Generation
### 4.4.1 Description and Priority
Uses AI to generate improved resume bullets and CV content. Priority: Medium.

### 4.4.2 Stimulus/Response Sequences
1. User requests resume enhancement or CV generation.
2. Server constructs prompts and calls the LLM provider.
3. Server returns structured output to the UI.

### 4.4.3 Functional Requirements
- REQ-11: The system shall generate enhanced resume bullets for a target role.
- REQ-12: The system shall generate CV sections (summary, skills, experience, projects).
- REQ-13: The system shall not invent experience and shall reuse profile data.

## 4.5 Job Matching and Tracking
### 4.5.1 Description and Priority
Matches job listings to the user and allows tracking. Priority: Medium.

### 4.5.2 Stimulus/Response Sequences
1. User requests matched jobs.
2. Server returns job list with similarity scores.
3. User tracks job status in the UI.

### 4.5.3 Functional Requirements
- REQ-14: The system shall return matched job listings with similarity scores.
- REQ-15: The system shall allow users to view and track job application status.

---

# 5. Other Nonfunctional Requirements

## 5.1 Performance Requirements
- The system shall return profile updates within 3 seconds under normal load.
- Career analysis shall complete within 5 minutes or return an async job status.
- Job matching shall return results within 10 seconds.

## 5.2 Safety Requirements
- The system shall prevent destructive operations without explicit user action.
- The system shall sanitize uploaded files and reject invalid types.

## 5.3 Security Requirements
- All endpoints shall require valid authentication tokens.
- User data shall be isolated per user ID.
- API keys and secrets shall be stored only in server-side environment variables.

## 5.4 Software Quality Attributes
- Availability: 99% uptime for development deployments.
- Reliability: Consistent output structure for all AI responses.
- Maintainability: Modular backend services and clear API boundaries.
- Usability: Simple, tab-based UI and clear messaging.

## 5.5 Business Rules
- Only authenticated users can access career analysis and resume features.
- Resume text overrides missing profile fields for analysis.
- Users may only access their own analysis results.

---

# 6. Other Requirements
- The system shall log major failures for debugging.
- The system shall allow environment-based configuration for external providers.

---

# Appendix A: Glossary
- ATS: Applicant Tracking System.
- LLM: Large Language Model.
- Embedding: Vector representation of text for similarity matching.
- RPC: Remote Procedure Call.

# Appendix B: Analysis Models
- Context diagram: UI -> API -> Data Services/LLM.
- Data flow: Resume upload -> Parsing -> Profile -> Embedding -> Matching -> Analysis.

# Appendix C: To Be Determined List
- TBD-1: Final production hosting and scaling targets.
- TBD-2: Compliance requirements for data privacy and retention.
- TBD-3: Formal UI/UX style guide references.
