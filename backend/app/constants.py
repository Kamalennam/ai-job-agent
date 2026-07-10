from enum import Enum


class ApplicationStatus(str, Enum):
    MATCHED = "matched"
    SAVED = "saved"
    DISMISSED = "dismissed"
    SELECTED = "selected"
    OPTIMIZING = "optimizing"
    READY = "ready"
    APPLYING = "applying"
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"


class ResumeStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"


class AutomationMode(str, Enum):
    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"


class JobSource(str, Enum):
    GREENHOUSE = "greenhouse"


class SchedulerRunStatus(str, Enum):
    STARTED = "started"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
