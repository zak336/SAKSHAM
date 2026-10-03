# SAKSHAM Setup Guide

### AI & LMS Enabled Cooperative Capacity Building, ERP & Employment Ecosystem

Complete setup instructions for Windows, Linux, and macOS.

SAKSHAM is an integrated digital ecosystem that connects learner identity, AI-assisted learning, attendance, offline learning, certification, skill-based job matching, placement tracking, and curriculum analytics.

The setup below follows the architecture and technology stack presented for Smart India Hackathon 2026. The system includes a Python backend, Flutter frontend, PostgreSQL, Redis, MinIO, AI/LLM processing, email/notification services, Raspberry Pi offline hubs, and ESP32/RFID attendance terminals.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Platform-Specific Prerequisites](#platform-specific-prerequisites)
- [Clone Repository](#clone-repository)
- [Backend Setup](#backend-setup)
- [Flutter Frontend Setup](#flutter-frontend-setup)
- [Database Setup](#database-setup)
- [Redis Setup](#redis-setup)
- [MinIO Setup](#minio-setup)
- [Environment Configuration](#environment-configuration)
- [AI Content Engine Setup](#ai-content-engine-setup)
- [Email and Notification Setup](#email-and-notification-setup)
- [Offline Raspberry Pi Hub Setup](#offline-raspberry-pi-hub-setup)
- [ESP32 RFID Attendance Setup](#esp32-rfid-attendance-setup)
- [Running the Application](#running-the-application)
- [Development with Docker](#development-with-docker)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [System Modules](#system-modules)
- [Next Steps](#next-steps)

---

## Prerequisites

### All Platforms

Install the following software before setting up SAKSHAM:

- **Git**: Version control
- **Python**: 3.10 or higher
- **Flutter**: Latest stable channel
- **PostgreSQL**: 14 or higher
- **Redis**: Latest stable
- **Docker Desktop / Docker Engine**: Recommended for local development
- **MinIO**: Object storage for videos, documents, certificates, and other media
- **Node.js**: Required only if the repository contains Node/TypeScript tooling
- **Arduino IDE or PlatformIO**: Required for ESP32 attendance terminal development

The prototype architecture also uses:

- Raspberry Pi for offline/remote learning hubs
- ESP32-based RFID attendance terminals
- RFID readers/cards/tags
- OpenAI/LLM-based processing
- Speech recognition / ASR for lecture and webinar audio
- Python-PPTX for extracting text from PPT files
- Resend for email delivery

---

## Platform-Specific Prerequisites

### Windows

#### 1. Python

Using Chocolatey:

```powershell
choco install python --version=3.10
```

Verify:

```powershell
python --version
```

#### 2. PostgreSQL

```powershell
choco install postgresql14
```

Or install PostgreSQL from the official PostgreSQL installer.

#### 3. Redis

Redis can be run through WSL2 or Docker.

Recommended:

```powershell
wsl --install
```

Then run Redis inside WSL, or use Docker as described later.

#### 4. Flutter

Download and extract the Flutter SDK.

Add:

```text
C:\flutter\bin
```

to PATH.

Verify:

```powershell
flutter doctor
```

#### 5. Docker

Install Docker Desktop and make sure Docker Engine is running.

Verify:

```powershell
docker --version
docker compose version
```

---

### Linux (Ubuntu/Debian)

#### 1. Python

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Verify:

```bash
python3 --version
```

#### 2. PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib
```

Start PostgreSQL:

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 3. Redis

```bash
sudo apt install redis-server
```

Start Redis:

```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### 4. Flutter

Install Flutter using the current stable release from the official Flutter documentation.

Add Flutter to PATH:

```bash
export PATH="$PATH:$HOME/flutter/bin"
```

Verify:

```bash
flutter doctor
```

#### 5. Docker

Install Docker Engine and Docker Compose.

Verify:

```bash
docker --version
docker compose version
```

---

### macOS

#### 1. Homebrew

If Homebrew is not installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Python

```bash
brew install python@3.10
```

Verify:

```bash
python3 --version
```

#### 3. PostgreSQL

```bash
brew install postgresql@14
brew services start postgresql@14
```

#### 4. Redis

```bash
brew install redis
brew services start redis
```

#### 5. Flutter

Install the latest stable Flutter SDK and add it to PATH:

```bash
export PATH="$PATH:$HOME/flutter/bin"
```

Verify:

```bash
flutter doctor
```

#### 6. Docker

Install Docker Desktop.

Verify:

```bash
docker --version
docker compose version
```

---

# Clone Repository

Clone the SAKSHAM repository:

```bash
git clone <repository-url>
cd saksham
```

If the repository uses a different directory name, replace `saksham` with the actual project directory.

---

# Backend Setup

The backend handles:

- Learner management
- APAAR-linked learner identity
- LMS and course management
- AI content generation
- Attendance
- Certification
- Skill taxonomy
- Job matching
- Placement tracking
- Placement analytics
- Offline synchronization
- Employer and trainer workflows

## 1. Create Python Virtual Environment

### Windows

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux/macOS

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -e .
```

If the project uses a requirements file instead:

```bash
pip install -r requirements.txt
```

The backend dependencies may include:

- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- PostgreSQL/async PostgreSQL driver
- Redis client
- MinIO/S3 client
- Python-PPTX
- ASR/Whisper-compatible libraries
- LLM/OpenAI SDK
- Cryptographic signing libraries
- Resend SDK
- Authentication/JWT libraries

Install only the dependencies defined by the repository's actual package configuration.

---

# Flutter Frontend Setup

SAKSHAM's user-facing interfaces support workflows for:

- Learners
- Trainers/faculty
- NCCT administrators
- Employers/recruiters

The frontend communicates with the backend API and displays learning, attendance, certification, job matching, placement, and analytics information.

## 1. Navigate to Project Root

```bash
cd saksham
```

## 2. Install Flutter Dependencies

```bash
flutter pub get
```

## 3. Configure API Endpoint

Edit the project's API configuration file.

Example:

```dart
class AppConfig {
  static const String apiBaseUrl = 'http://localhost:8000';
}
```

For a physical device, replace `localhost` with the development machine's LAN IP address.

Example:

```dart
static const String apiBaseUrl = 'http://192.168.1.100:8000';
```

## 4. Generate Code if Required

If the project uses `build_runner`:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## 5. Verify Flutter

```bash
flutter doctor -v
```

---

# Database Setup

SAKSHAM uses a relational database for centralized learner, course, attendance, certification, skill, job, application, and analytics data.

## Create Database and User

### Windows

```powershell
psql -U postgres
```

Inside PostgreSQL:

```sql
CREATE DATABASE saksham;
CREATE USER saksham_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE saksham TO saksham_user;
\q
```

### Linux

```bash
sudo -u postgres psql
```

Then:

```sql
CREATE DATABASE saksham;
CREATE USER saksham_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE saksham TO saksham_user;
\q
```

### macOS

```bash
psql postgres
```

Then:

```sql
CREATE DATABASE saksham;
CREATE USER saksham_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE saksham TO saksham_user;
\q
```

## Run Migrations

With the backend virtual environment activated:

```bash
alembic current
alembic upgrade head
alembic history --verbose
```

---

# Redis Setup

Redis is used for fast temporary data, caching, background processing, synchronization queues, or notification batching depending on the implementation.

Verify Redis:

```bash
redis-cli ping
```

Expected:

```text
PONG
```

Example environment variable:

```env
REDIS_URL=redis://localhost:6379/0
```

---

# MinIO Setup

MinIO provides S3-compatible object storage for application files such as:

- Lecture videos
- PPT files
- Generated notes
- Quiz-related assets
- Certificates
- Offline learning packages
- Other uploaded documents/media

## Run MinIO with Docker

```bash
docker run -d \
  --name saksham-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=change-this-password \
  quay.io/minio/minio server /data --console-address ":9001"
```

MinIO API:

```text
http://localhost:9000
```

MinIO Console:

```text
http://localhost:9001
```

Create a bucket for SAKSHAM, for example:

```text
saksham-media
```

Example configuration:

```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=change-this-password
MINIO_BUCKET=saksham-media
MINIO_SECURE=false
```

Use strong credentials outside local development.

---

# Environment Configuration

Create a `.env` file from the repository's example file.

### Windows

```powershell
copy .env.example .env
notepad .env
```

### Linux/macOS

```bash
cp .env.example .env
nano .env
```

Example configuration:

```env
# Application
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://saksham_user:your_password@localhost:5432/saksham

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=change-this-password
MINIO_BUCKET=saksham-media
MINIO_SECURE=false

# AI / LLM
OPENAI_API_KEY=your-api-key

# Email
RESEND_API_KEY=your-api-key
RESEND_FROM_EMAIL=your-verified-sender@example.com

# Optional external integrations
NCS_API_URL=
INDEED_API_URL=
INTERNSHALA_API_URL=
```

Do not commit `.env` or API keys to Git.

External employment-platform integrations shown in the project presentation are future scope and should remain disabled until the required APIs, credentials, permissions, and integration code are available.

---

# AI Content Engine Setup

The AI-assisted learning module converts lecture/webinar audio and PPT material into structured learning content.

The architecture shown in the project presentation uses:

```text
Lecture/Webinar Audio
        |
        v
Speech Recognition / ASR
        |
        +------------------+
        |                  |
        v                  v
PPT Text Extraction     Transcript
(Python-PPTX)              |
        |                  |
        +--------+---------+
                 |
                 v
          LLM Processing
                 |
        +--------+--------+
        |                 |
        v                 v
 Structured Notes     Topic-wise Quiz
        |
        v
 Trainer Review
        |
        v
 Multilingual Publishing
```

## PPT Processing

The application can use Python-PPTX to extract text from uploaded PowerPoint files.

Example dependency:

```bash
pip install python-pptx
```

## Speech Recognition

Install the ASR dependencies defined by the project.

The prototype architecture uses Whisper-class/multilingual speech recognition for lecture and webinar audio.

The final implementation should use the exact ASR package and model specified by the repository.

## LLM Processing

Configure the required LLM provider/API key in `.env`.

The AI engine should support:

- Structured note generation
- Topic extraction
- Question generation
- Quiz generation
- Multilingual content generation

Generated content should pass through trainer/faculty review before publication, as shown in the proposed architecture.

---

# Digital Certificate Setup

SAKSHAM generates digitally signed certificates after program completion.

The certificate workflow is:

```text
Program Completion
       |
       v
Certificate Generation
       |
       v
Digital Signature
       |
       v
Certificate Delivered
       |
       v
Employer Verification
       |
       v
Public-Key Signature Check
```

The signing key must be stored securely and should not be included in the repository.

Example environment configuration:

```env
CERTIFICATE_SIGNING_KEY_PATH=/secure/path/private_key.pem
CERTIFICATE_PUBLIC_KEY_PATH=/secure/path/public_key.pem
```

Only the authorized issuing institution should control the private signing key.

The employer dashboard can verify the certificate using the corresponding public key.

For printed/scanned certificates where the embedded signature is unavailable, the prototype presentation specifies a manual Certificate ID lookup as a fallback verification method.

---

# Skill Taxonomy and Job Matching

The job matching engine uses a hierarchical skill taxonomy instead of relying only on keyword matching.

The prototype architecture includes:

```text
Skill Taxonomy
      |
      v
Closure Table
      |
      v
Precomputed Skill Expansion
      |
      v
Inverted Index
      |
      v
Fast Learner Lookup
      |
      v
Preference / Hard Filters
      |
      v
Job Match
```

Employers can define:

- Required skills
- Location
- Shift timing
- Salary range
- Other supported preferences

The learner receives matching job notifications based on the configured matching rules.

The implementation should preserve exact and explainable skill mappings.

---

# Attendance Setup

SAKSHAM supports two attendance modes.

## On-Campus Attendance

The presentation specifies:

```text
ESP32
  |
RFID Reader
  |
Student RFID Card/Tag
  |
APAAR-linked Learner Record
  |
Attendance Dashboard
```

A learner taps their RFID card/tag on the terminal.

The ESP32 sends the attendance event to the backend when network connectivity is available.

The system should support offline buffering where implemented.

## Online / Remote Attendance

Online attendance uses engagement signals such as:

- Video progress
- Play/pause events
- Seek events
- Tab visibility
- Quiz completion

These signals are used to determine learner engagement rather than relying only on a video-open event.

---

# ESP32 RFID Attendance Setup

## Required Hardware

- ESP32 development board
- Compatible RFID reader
- RFID cards/tags
- USB cable
- Wi-Fi network
- Optional enclosure/power supply

## Development Environment

Install Arduino IDE or PlatformIO.

Configure:

- ESP32 board package
- RFID reader library
- Wi-Fi configuration
- SAKSHAM attendance API endpoint

Example configuration:

```cpp
const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";

const char* API_BASE_URL = "http://YOUR_SERVER_IP:8000";
```

Do not hard-code production credentials into firmware.

## Attendance Flow

```text
RFID Tap
   |
Read Card UID
   |
Map UID to Learner
   |
Create Attendance Event
   |
Send to API
   |
Store/Buffer if Offline
   |
Synchronize when Online
```

The exact RFID reader model and GPIO wiring should follow the hardware used by the repository.

---

# Offline Raspberry Pi Hub Setup

The offline/remote access layer uses Raspberry Pi hubs to provide learning content in low or zero-connectivity locations.

The architecture shown in the presentation uses:

```text
Central Server
      |
Pre-Processed Content Push
      |
      v
Raspberry Pi Hub
      |
Local Wi-Fi Access Point
      |
      +--> Learners
      |
      +--> Videos
      +--> Notes
      +--> Quizzes
      |
Quiz Answers / Progress
      |
Local Buffer / Delta Sync Queue
      |
      v
Central Server
```

## Required Hardware

- Raspberry Pi
- MicroSD card or suitable storage
- Power supply
- Wi-Fi capability
- Optional Ethernet connection
- Local client devices

## Basic Setup

Install Raspberry Pi OS and update:

```bash
sudo apt update
sudo apt upgrade -y
```

Install the services required by the offline hub implementation.

The hub should provide:

- Local content server
- Local Wi-Fi access
- Cached learning content
- Quiz access
- Local learner progress storage
- Synchronization queue

The exact networking and synchronization implementation should follow the repository configuration.

---

# Placement Tracking

The application tracks the placement funnel:

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

Each stage should retain a timestamped application status log.

This data is used by the analytics engine.

---

# Placement Analytics

The analytics engine described in the project presentation includes:

### Funnel Conversion Rate

Calculates the percentage of applications progressing through each stage.

Example:

```text
Applied -> Shortlisted -> Interviewed -> Hired
```

### Skill Lift Score

Compares skill frequency among hired candidates against all applicants to identify skills associated with hiring outcomes.

### Skill-Gap Analysis

Compares:

```text
Job-required Skills
        vs.
Course Catalogue / Taught Skills
```

This can identify skills that are demanded by jobs but are not sufficiently represented in training.

### Skill Combination Analysis

Examines combinations of skills present in hired candidates to identify useful skill combinations for curriculum design.

The dashboard presents these results through graphs and analytics views.

---

# Email and Notification Setup

The project technology stack includes Resend for email delivery.

The notification system can be used for:

- Matching job notifications
- Application updates
- Certification notifications
- Other supported learner/employer communications

Example:

```env
RESEND_API_KEY=your-api-key
RESEND_FROM_EMAIL=verified@example.com
```

The architecture specifies batching notifications rather than sending each learner notification synchronously one by one.

Example conceptual flow:

```text
Match Results
     |
     v
Notification Queue
     |
     v
Batch Email Processing
     |
     v
Resend
```

---

# Running the Application

## Start PostgreSQL

Make sure PostgreSQL is running.

## Start Redis

Make sure Redis is running:

```bash
redis-cli ping
```

## Start MinIO

If running with Docker:

```bash
docker start saksham-minio
```

## Start Backend

### Windows

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Linux/macOS

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

## Start Flutter

Run on Chrome:

```bash
flutter run -d chrome
```

List devices:

```bash
flutter devices
```

Run on a specific device:

```bash
flutter run -d <device-id>
```

Android emulator:

```bash
flutter run -d android
```

Windows desktop:

```bash
flutter run -d windows
```

macOS desktop:

```bash
flutter run -d macos
```

Linux desktop:

```bash
flutter run -d linux
```

---

# Development with Docker

Docker is recommended when you want a reproducible development environment.

## Prerequisites

- Docker Desktop on Windows/macOS
- Docker Engine on Linux
- Docker Compose

## Start Services

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f
```

Stop services:

```bash
docker compose down
```

Stop services and remove volumes:

```bash
docker compose down -v
```

**Warning:** Removing volumes may permanently delete local development database and object-storage data.

A typical local environment may expose:

```text
Backend API:  http://localhost:8000
PostgreSQL:   localhost:5432
Redis:        localhost:6379
MinIO API:    http://localhost:9000
MinIO Console:http://localhost:9001
```

The actual ports should be taken from the repository's `docker-compose.yml` or `compose.yaml`.

---

# Verification

## Verify Backend

```bash
curl http://localhost:8000/health
```

Open API documentation:

```text
http://localhost:8000/docs
```

## Verify Database

```bash
psql -U saksham_user -d saksham -h localhost
```

List tables:

```sql
\dt
```

Exit:

```sql
\q
```

## Verify Redis

```bash
redis-cli ping
```

Expected:

```text
PONG
```

## Verify MinIO

Open:

```text
http://localhost:9001
```

Confirm that the SAKSHAM storage bucket exists.

## Verify Flutter

```bash
flutter doctor -v
flutter test
```

## Verify ESP32

Confirm:

1. ESP32 connects to Wi-Fi.
2. RFID reader detects a card/tag.
3. Card UID is read correctly.
4. Attendance API receives the event.
5. Learner attendance appears in the dashboard.
6. Offline buffering works if implemented.
7. Buffered events synchronize after connectivity returns.

## Verify Raspberry Pi Hub

Confirm:

1. Raspberry Pi boots correctly.
2. Local Wi-Fi is available.
3. Learning content can be opened without internet.
4. Videos, notes, and quizzes are accessible.
5. Quiz/progress data is stored locally.
6. Synchronization occurs when connectivity returns.

---

# Troubleshooting

## Windows PowerShell Execution Policy

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Python Not Found

Verify:

```powershell
python --version
```

If Python is installed but unavailable, add its installation directory and Scripts directory to PATH.

## PostgreSQL Connection Error

Check:

- PostgreSQL is running
- Database name is correct
- Username and password are correct
- Port is correct
- `DATABASE_URL` is correct

## Redis Connection Error

Verify:

```bash
redis-cli ping
```

If Redis is unavailable, check the service or Docker container.

## MinIO Connection Error

Verify the container:

```bash
docker ps
```

Check:

```text
http://localhost:9000
```

and:

```text
http://localhost:9001
```

Also verify the endpoint, access key, secret key, and bucket configuration.

## Migration Errors

Check migration status:

```bash
alembic current
```

Run:

```bash
alembic upgrade head
```

For local development only, a database reset may be performed if supported by the project.

**Warning:** Resetting the database can delete data.

## Flutter Build Errors

```bash
flutter clean
flutter pub get
flutter pub upgrade
```

Then run:

```bash
flutter run
```

## API Not Reachable from Physical Device

Do not use:

```text
localhost
```

for the backend address on a physical phone or ESP32.

Use the development computer's LAN IP:

```text
http://192.168.x.x:8000
```

Make sure the firewall allows the backend port.

## Port Already in Use

### Windows

```powershell
netstat -ano | findstr :8000
```

Kill the process:

```powershell
taskkill /PID <PID> /F
```

### Linux/macOS

```bash
lsof -i :8000
```

Kill:

```bash
kill -9 <PID>
```

---

# System Modules

| Module | Purpose |
|---|---|
| Unified Learner Identity | APAAR-linked centralized learner identity |
| Learner Management | Learner profiles and records |
| LMS | Courses and learning content |
| AI Content Engine | Notes and quiz generation |
| Multilingual Publishing | Publishing learning content in multiple languages |
| Attendance | ESP32/RFID and engagement-based attendance |
| Offline Learning | Raspberry Pi-based content delivery |
| Certification | Digitally signed certificate generation and verification |
| Skill Taxonomy | Hierarchical skill representation |
| Job Matching | Skill-based employment matching |
| Employer Dashboard | Job posting and learner discovery |
| Placement Tracking | Application funnel tracking |
| Analytics | Placement and curriculum analytics |
| Notification System | Job and system notifications |
| Object Storage | Videos, documents, certificates, and media |
| Synchronization | Offline-to-online data synchronization |

---

# Architecture Overview

The high-level system follows the architecture presented in the SIH 2026 proposal:

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

Offline access:

```text
Central Platform
      |
      v
Raspberry Pi Hub
      |
      v
Local Wi-Fi
      |
      v
Learners
      |
      v
Local Progress
      |
      v
Delta Synchronization
      |
      v
Central Platform
```

---

# Security Notes

## API Keys

Never commit:

- OpenAI API keys
- Resend API keys
- Database passwords
- JWT secrets
- MinIO credentials
- Certificate private keys
- Wi-Fi credentials

Use `.env` or a secure secret-management system.

## Certificate Private Key

The certificate signing private key must remain under the control of the authorized issuing institution.

Never upload the private key to GitHub or store it inside the Flutter application.

## APAAR and Learner Data

Learner identity and training information should be handled according to the applicable institutional, government, privacy, and data-protection requirements.

Only store and process the data required by the application's authorized workflows.

---

# Next Steps

After completing the local setup:

1. Create or configure the initial administrator account.
2. Configure the learner identity workflow.
3. Configure course and training data.
4. Configure the hierarchical skill taxonomy.
5. Seed development/test skills and jobs.
6. Configure AI content generation.
7. Configure trainer review and approval.
8. Configure certificate signing for development.
9. Configure employer job posting and matching.
10. Configure placement funnel tracking.
11. Configure analytics dashboards.
12. Configure the Raspberry Pi offline hub.
13. Configure ESP32 RFID attendance terminals.
14. Test offline synchronization.
15. Test certificate verification.
16. Test job matching and notification workflows.

---

# External Integrations and Future Scope

The project presentation identifies integration with government and private employment platforms as future scope.

Potential platforms mentioned in the proposal include:

- National Career Service
- Indeed
- Internshala

These integrations should only be enabled after the required API access, authentication, permissions, terms of service, and implementation are available.

---

# Project Information

**Project:** SAKSHAM

**Problem Statement:** SIH26087

**Problem Statement Title:** AI & LMS Enabled Cooperative Capacity Building, ERP & Employment Ecosystem

**Theme:** Smart Education

**PS Category:** Hardware

**Team:** Clever Codex

**Team ID:** 141881

**Hackathon:** Smart India Hackathon 2026

---

<p align="center">
Built by <strong>Clever Codex</strong> for Smart India Hackathon 2026
</p>
