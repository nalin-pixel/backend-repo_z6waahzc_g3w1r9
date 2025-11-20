"""
Database Schemas for ERFMS (Energy Renovation File Management SaaS)

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name, e.g. Project -> "project".
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import date, datetime

# Core users of the platform (internal staff + client contacts)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    role: Literal["admin", "manager", "auditor", "client"] = Field("client", description="User role")
    is_active: bool = Field(True, description="Whether user is active")

# Client company/person for whom projects are executed
class Client(BaseModel):
    name: str = Field(..., description="Client name or company")
    contact_email: Optional[EmailStr] = Field(None, description="Primary contact email")
    contact_phone: Optional[str] = Field(None, description="Primary contact phone")
    address: Optional[str] = Field(None, description="Postal address")
    notes: Optional[str] = Field(None, description="Internal notes")

# Base document metadata stored in DB (files can be stored in external storage, this keeps metadata and link)
class Document(BaseModel):
    project_id: Optional[str] = Field(None, description="Related project id")
    title: str = Field(..., description="Document title")
    doc_type: Literal[
        "quote",
        "invoice",
        "contract",
        "photo",
        "audit_report",
        "cee_attachment",
        "mar_attachment",
        "other"
    ] = Field("other", description="Type of the document")
    url: Optional[str] = Field(None, description="Public/secure URL to the file")
    version: Optional[int] = Field(1, ge=1, description="Version number")
    notes: Optional[str] = Field(None, description="Notes or description")

# Project entity
class Project(BaseModel):
    title: str = Field(..., description="Project title")
    client_id: Optional[str] = Field(None, description="Client reference (id)")
    manager_id: Optional[str] = Field(None, description="Assigned project manager (user id)")
    status: Literal[
        "draft",
        "in_progress",
        "awaiting_documents",
        "awaiting_approval",
        "completed",
        "archived"
    ] = Field("draft", description="Overall project status")
    start_date: Optional[date] = Field(None, description="Planned start date")
    due_date: Optional[date] = Field(None, description="Planned due date")
    budget_eur: Optional[float] = Field(None, ge=0, description="Budget in EUR")
    description: Optional[str] = Field(None, description="Short description")

# Lightweight task for workflow tracking
class Task(BaseModel):
    project_id: str = Field(..., description="Related project id")
    title: str = Field(..., description="Task title")
    assignee_id: Optional[str] = Field(None, description="User responsible")
    due_date: Optional[date] = Field(None, description="Due date")
    status: Literal["todo", "in_progress", "blocked", "done"] = Field("todo")

# CEE application tracking
class CEEApplication(BaseModel):
    project_id: str = Field(..., description="Related project id")
    status: Literal["draft", "submitted", "awaiting_approval", "approved", "rejected"] = Field("draft")
    submission_date: Optional[date] = Field(None)
    approval_date: Optional[date] = Field(None)
    cee_volume_kwh: Optional[float] = Field(None, ge=0, description="CEE volume (kWh cumac)")
    cee_value_eur: Optional[float] = Field(None, ge=0, description="Estimated/actual value in EUR")

# MAR application tracking (Ma Prime Rénov')
class MARApplication(BaseModel):
    project_id: str = Field(..., description="Related project id")
    status: Literal[
        "pre_application",
        "submitted",
        "awaiting_instruction",
        "instruction_in_progress",
        "grant_awarded",
        "payment_received"
    ] = Field("pre_application")
    amount_eur: Optional[float] = Field(None, ge=0)
    last_update: Optional[datetime] = Field(None)

# Energy audit tracking
class Audit(BaseModel):
    project_id: str = Field(..., description="Related project id")
    status: Literal["scheduled", "in_progress", "report_generated", "client_reviewed"] = Field("scheduled")
    scheduled_date: Optional[date] = Field(None)
    auditor_id: Optional[str] = Field(None)
    report_document_id: Optional[str] = Field(None, description="Document id for audit report")

# The schema endpoint consumer expects to read these classes
__all__ = [
    "User",
    "Client",
    "Document",
    "Project",
    "Task",
    "CEEApplication",
    "MARApplication",
    "Audit",
]
