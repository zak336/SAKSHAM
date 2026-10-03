# SAKSHAM

### AI & LMS Enabled Cooperative Capacity Building, ERP & Employment Ecosystem

SAKSHAM is an integrated digital ecosystem designed to connect **learning, training, attendance, certification, skill development, and employment** on a unified platform.

Developed for **Smart India Hackathon 2026** by **Clever Codex**.

## Problem Statement

**SIH26087**  
**Theme:** Smart Education  
**Category:** Hardware  
**Team ID:** 141881  
**Team:** Clever Codex

SAKSHAM addresses fragmented training ecosystems by connecting learner identity, AI-assisted learning, attendance, offline learning, certification, skill-based employment matching, placement tracking, and curriculum analytics.

## Key Features

- **Unified Learner Identity** using APAAR ID
- **AI-Assisted Learning** for lecture, webinar, and PPT content
- **Multilingual Learning Content**
- **Offline Learning** through Raspberry Pi hubs
- **Smart Attendance** using ESP32/RFID and online engagement tracking
- **Digitally Signed Certificates**
- **Hierarchical Skill Taxonomy**
- **Skill-Based Job Matching**
- **Employer Dashboard**
- **Placement Funnel Tracking**
- **Placement Analytics**
- **Curriculum Feedback Loop**

## System Architecture

```text
Learners / Trainers / NCCT Admins / Employers
                    |
                    v
             APAAR-linked ID
                    |
                    v
             Relational DB
                    |
      +-------------+-------------+
      |             |             |
      v             v             v
 AI Learning    Attendance    Certification
      |             |             |
      +-------------+-------------+
                    |
                    v
              Skill Profile
                    |
                    v
             Job Match Engine
                    |
                    v
           Placement Tracking
                    |
                    v
           Placement Analytics
                    |
                    v
          Curriculum Feedback
```

## Technology Stack

- Python
- TypeScript
- Flutter
- PostgreSQL
- Redis
- MinIO
- Docker
- Raspberry Pi
- ESP32
- RFID
- OpenAI / LLM-based processing
- Speech Recognition / ASR
- Python-PPTX
- Resend

## Repository Structure

The exact structure may vary depending on the implementation, but the project is organized around the following major components:

```text
saksham/
│
├── backend/              # Backend API and core services
├── frontend/             # Flutter application
├── esp32/                # ESP32/RFID attendance firmware
├── raspberry-pi/         # Offline learning hub components
├── docs/                 # Project documentation
├── docker-compose.yml    # Local development services
├── .env.example          # Environment configuration template
├── README.md             # Project overview
└── SETUP.md              # Complete setup instructions
```

## Getting Started

Before running the project, **read the complete [`SETUP.md`](./SETUP.md) file first**.

The setup guide contains the detailed instructions for:

- Installing prerequisites
- Setting up Python and the backend
- Setting up Flutter
- Configuring PostgreSQL
- Configuring Redis
- Setting up MinIO
- Configuring environment variables
- Setting up the AI Content Engine
- Configuring digital certificate signing
- Configuring skill-based job matching
- Setting up ESP32/RFID attendance
- Setting up Raspberry Pi offline learning hubs
- Running the application
- Running the project with Docker
- Verifying each component
- Troubleshooting common issues

### Quick Setup

```bash
git clone <repository-url>
cd saksham
```

Then follow:

```text
SETUP.md
```

Do not rely on this README for the complete installation process. **`SETUP.md` is the source of truth for project setup and configuration.**

## Core Modules

| Module | Purpose |
|---|---|
| Learner Management | Centralized learner records |
| APAAR Integration | Unified learner identity |
| LMS | Courses and learning content |
| AI Content Engine | Notes and quiz generation |
| Multilingual Publishing | Learning content in multiple languages |
| Attendance | RFID and engagement-based attendance |
| Offline Learning | Raspberry Pi-based content delivery |
| Certification | Digital certificate generation and verification |
| Skill Taxonomy | Hierarchical skill representation |
| Job Matching | Skill-based employment matching |
| Employer Dashboard | Job posting and learner discovery |
| Placement Tracking | Application funnel tracking |
| Analytics | Placement and curriculum analytics |
| Notification System | Job and system notifications |

## AI-Assisted Learning

SAKSHAM can process:

```text
Lecture / Webinar Audio
          +
      PPT Slides
          |
          v
   AI Processing Engine
          |
    +-----+-----+
    |           |
    v           v
Structured    Topic-wise
   Notes        Quizzes
    |           |
    +-----+-----+
          |
          v
    Trainer Review
          |
          v
Multilingual Publishing
```

The system uses speech recognition for audio and Python-PPTX for extracting text from PowerPoint presentations. LLM-based processing then generates structured notes and topic-wise quizzes.

## Offline Learning

Raspberry Pi hubs allow learners to access:

- Videos
- Notes
- Quizzes
- Learning material

without continuous internet connectivity.

Learner progress can be stored locally and synchronized with the central system once connectivity becomes available.

## Smart Attendance

### On-Campus

```text
RFID Card
    |
    v
ESP32 RFID Terminal
    |
    v
Attendance API
    |
    v
Learner Record
    |
    v
Attendance Dashboard
```

### Online

Online attendance can use engagement signals including:

- Video progress
- Play/pause events
- Seek events
- Tab visibility
- Quiz completion

## Digital Certificates

Certificates are digitally signed using an authorized institutional private key.

Verification uses the corresponding public key:

```text
Certificate
     |
     v
Signature Verification
     |
 +---+---+
 |       |
Valid   Invalid
```

The private signing key must never be committed to the repository.

## Skill-Based Employment

SAKSHAM uses a hierarchical skill taxonomy instead of relying only on keyword matching.

```text
Job Requirements
       |
       v
Skill Taxonomy
       |
       v
Skill Expansion
       |
       v
Learner Skill Profiles
       |
       v
Matching Engine
       |
       v
Relevant Learners
```

The system can also consider employer preferences such as location, shift timing, and salary range.

## Placement Analytics

SAKSHAM tracks the application funnel:

```text
Applied
   |
   v
Shortlisted
   |
   v
Interviewed
   |
   +----> Rejected
   |
   v
Hired
```

Analytics can then be used to study:

- Funnel conversion rates
- Skills associated with hiring
- Skill gaps between jobs and courses
- Useful combinations of skills

This creates a feedback loop for improving training curricula.

## Security

Never commit sensitive credentials to the repository.

Do not commit:

```text
.env
API keys
Database passwords
JWT secrets
MinIO credentials
Certificate private keys
Wi-Fi credentials
```

Use `.env` and appropriate secret-management mechanisms for development and production.

Learner and identity data should be handled according to applicable institutional, government, privacy, and data-protection requirements.

## Future Scope

The project presentation identifies future integration with employment platforms such as:

- National Career Service
- Indeed
- Internshala

These integrations should only be enabled when the required APIs, authentication, permissions, and implementation are available.

## Documentation

### Setup Guide

**Start here before running the project:**

[SETUP.md](./SETUP.md)

The setup guide contains the complete platform-specific installation, configuration, hardware setup, database setup, Docker setup, verification, and troubleshooting instructions.

### Project Presentation

The SIH 2026 presentation contains the project's:

- Problem overview
- Proposed solution
- Technical approach
- System architecture
- Feasibility and viability
- Impact and benefits
- Future scope
- Prototype working flow

## Project Information

**Project:** SAKSHAM  
**Problem Statement:** SIH26087  
**Theme:** Smart Education  
**Category:** Hardware  
**Team:** Clever Codex  
**Team ID:** 141881  
**Hackathon:** Smart India Hackathon 2026

---

<p align="center">
Built by <strong>Clever Codex</strong> for Smart India Hackathon 2026
</p>