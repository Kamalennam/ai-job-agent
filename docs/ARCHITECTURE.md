# Architecture Diagram — AI Job Agent

**Version**: 0.1.0  
**Last Updated**: 2026-07-10

> Export this diagram to `ARCHITECTURE.png` for the docs folder. Use Mermaid Live Editor or `mmdc` CLI.

---

## System Context

```mermaid
graph TB
    User[Job Seeker Browser]
    
    subgraph "Docker Compose Stack"
        Nginx[Nginx :80]
        
        subgraph "Frontend"
            React[React SPA<br/>Vite + TypeScript + Tailwind]
        end
        
        subgraph "Backend"
            API[FastAPI API :8000]
            CeleryWorker[Celery Workers]
            CeleryBeat[Celery Beat Scheduler]
            APSched[APScheduler]
        end
        
        subgraph "Data Stores"
            MongoDB[(MongoDB :27017)]
            Redis[(Redis :6379)]
        end
        
        subgraph "AI & Automation"
            Ollama[Ollama :11434<br/>llama3.2 + nomic-embed-text]
            Playwright[Playwright<br/>Browser Automation]
        end
    end
    
    subgraph "External Sources"
        GH[Greenhouse]
        LV[Lever]
        AS[Ashby]
        LI[LinkedIn]
        IN[Indeed]
        NK[Naukri]
        WF[Wellfound]
        CS[Company Sites]
    end
    
    SMTP[SMTP / Gmail]
    
    User -->|HTTPS| Nginx
    Nginx --> React
    Nginx -->|/api/*| API
    React -->|REST| API
    
    API --> MongoDB
    API --> Redis
    API --> CeleryWorker
    
    CeleryBeat --> Redis
    APSched --> CeleryWorker
    CeleryWorker --> Redis
    CeleryWorker --> MongoDB
    CeleryWorker --> Ollama
    CeleryWorker --> Playwright
    CeleryWorker --> SMTP
    
    CeleryWorker --> GH
    CeleryWorker --> LV
    CeleryWorker --> AS
    CeleryWorker --> LI
    CeleryWorker --> IN
    CeleryWorker --> NK
    CeleryWorker --> WF
    CeleryWorker --> CS
```

---

## Pipeline Flow

```mermaid
flowchart LR
    A[Register] --> B[Upload Resume]
    B --> C[Parse Resume]
    C --> D[Generate Embedding]
    D --> E[Collect Jobs]
    E --> F[AI Match]
    F --> G[Select Resume]
    G --> H[Optimize Resume]
    H --> I[ATS Apply]
    I --> J[Discover Recruiter]
    J --> K[Send Email]
    I --> L[Analytics]
    F --> M[Notifications]
    K --> M
```

---

## Backend Layer Architecture

```mermaid
graph TD
    subgraph "API Layer"
        R1[auth/]
        R2[resumes/]
        R3[jobs/]
        R4[applications/]
        R5[analytics/]
    end
    
    subgraph "Service Layer"
        S1[AuthService]
        S2[ResumeService]
        S3[JobService]
        S4[ApplicationService]
        S5[AnalyticsService]
        S6[ATSService]
        S7[EmailService]
    end
    
    subgraph "Data Layer"
        REPO[Repositories]
        MODELS[Beanie Models]
    end
    
    subgraph "Async Layer"
        W1[resume_worker]
        W2[scraping_worker]
        W3[ai_worker]
        W4[ats_worker]
        W5[analytics_worker]
        W6[notification_worker]
    end
    
    subgraph "AI Layer"
        AI1[Ollama Client]
        AI2[Embeddings]
        AI3[Prompts]
        AI4[Resume Matching]
        AI5[Cover Letter]
    end
    
    R1 --> S1
    R2 --> S2
    R3 --> S3
    R4 --> S4
    R5 --> S5
    
    S1 --> REPO
    S2 --> REPO
    S2 --> W1
    S3 --> REPO
    S3 --> W2
    S4 --> REPO
    S4 --> W4
    S5 --> REPO
    
    W1 --> S2
    W2 --> S3
    W3 --> AI4
    W4 --> S6
    W5 --> S5
    W6 --> S7
    
    AI4 --> AI1
    AI4 --> AI3
    AI5 --> AI1
    
    REPO --> MODELS
```

---

## Celery Queue Topology

```mermaid
graph LR
    Redis[(Redis Broker)]
    
    Redis --> Q1[resume]
    Redis --> Q2[scraping]
    Redis --> Q3[matching]
    Redis --> Q4[ai]
    Redis --> Q5[ats]
    Redis --> Q6[analytics]
    Redis --> Q7[notifications]
    Redis --> Q8[maintenance]
    
    Q1 --> W1[resume_parser_worker]
    Q2 --> W2[job_scraper_worker]
    Q3 --> W3[job_match_worker]
    Q4 --> W4[cover_letter_worker<br/>resume_optimizer_worker]
    Q5 --> W5[ats_apply_worker]
    Q6 --> W6[analytics_worker]
    Q7 --> W7[notification_worker]
    Q8 --> W8[cleanup_worker]
```

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial architecture diagrams |
