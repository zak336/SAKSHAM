# SAKSHAM

### AI & LMS Enabled Cooperative Capacity Building, ERP & Employment Ecosystem

SAKSHAM is an integrated digital ecosystem designed to connect learning, training, attendance, certification, skill development, and employment on a unified platform.

Developed for **Smart India Hackathon 2026**.

## Problem Statement

**SIH26087**  
**Theme:** Smart Education  
**Category:** Hardware  
**Team:** Clever Codex  
**Team ID:** 141881

Training ecosystems are often fragmented across learner registration, attendance, learning platforms, certification, and employment systems. SAKSHAM addresses this fragmentation by creating a unified learner ecosystem that connects training with employment outcomes.

## Key Features

### Unified Learner Identity
Uses the learner's existing **APAAR ID** to connect registration, attendance, learning progress, certification, skills, and employment records.

### AI-Assisted Learning
Converts lectures, webinars, and PPT presentations into structured notes and topic-wise quizzes using AI.

### Multilingual Content
Generates and publishes learning content in multiple languages.

### Offline Learning
Raspberry Pi-based local hubs provide access to videos, notes, and quizzes in low or zero-connectivity areas. Data can synchronize when connectivity becomes available.

### Smart Attendance
Supports both:

- ESP32-based RFID attendance for on-campus learners
- Engagement-based attendance for online learners using video progress, play/pause events, tab visibility, and quiz completion

### Digitally Signed Certificates
Certificates can be digitally signed using an institutional private key and verified using the corresponding public key.

### Skill-Based Job Matching
Uses a hierarchical skill taxonomy to match learners with relevant job opportunities instead of relying only on keyword matching.

### Employer Dashboard
Employers can post jobs, define required skills, specify preferences, and discover suitable learners.

### Placement Tracking
Tracks the complete application funnel:

`Applied → Shortlisted → Interviewed → Hired/Rejected`

### Placement Analytics
Analyzes placement data to identify:

- Course funnel conversion rates
- Skills associated with hiring
- Skill gaps between training and industry requirements
- Useful combinations of skills

This creates a feedback loop between employment outcomes and curriculum development.

## System Architecture

```text
Learners / Trainers / Employers
              |
              v
       Unified Learner ID
          (APAAR ID)
              |
              v
       Relational Database
              |
     +--------+--------+
     |        |        |
     v        v        v
    AI     Attendance  Certification
 Learning    Module      System
     |        |        |
     +--------+--------+
              |
              v
       Skill Profile
              |
              v
        Job Matching
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

## Core Modules

| Module | Purpose |
|---|---|
| Learner Management | Centralized learner records |
| APAAR Integration | Unified learner identity |
| LMS | Courses and learning content |
| AI Content Engine | Notes and quiz generation |
| Attendance | RFID and engagement-based attendance |
| Offline Learning | Raspberry Pi-based content delivery |
| Certification | Digital certificate generation and verification |
| Skill Taxonomy | Hierarchical skill representation |
| Job Matching | Skill-based employment matching |
| Employer Dashboard | Job posting and candidate discovery |
| Placement Tracking | Application funnel tracking |
| Analytics | Placement and curriculum analytics |

## Impact

SAKSHAM aims to:

- Reduce fragmentation across training systems
- Improve access to learning in low-connectivity areas
- Reduce manual content preparation
- Improve certificate verification
- Connect learners with relevant employment opportunities
- Provide data-driven insights for curriculum improvement
- Scale across additional training institutes and offline learning hubs

## Future Scope

Future versions can integrate with government and private employment platforms such as National Career Service, Indeed, and Internshala to provide additional job opportunities and automated notifications to learners.

## Team

**Clever Codex**  
Smart India Hackathon 2026

**Problem Statement:** SIH26087  
**Team ID:** 141881

---

<p align="center">
Built by <strong>Clever Codex</strong> for Smart India Hackathon 2026
</p>