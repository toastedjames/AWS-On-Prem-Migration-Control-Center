from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Float
from sqlalchemy import DateTime

from datetime import datetime

from database import Base


# =========================================================
# APPLICATION
# =========================================================

class Application(Base):

    __tablename__ = "applications"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    name = Column(
        String(200),
        nullable=False
    )


    description = Column(
        Text
    )


    source_environment = Column(
        String(100),
        default="AWS"
    )


    target_environment = Column(
        String(100),
        default="ON_PREM"
    )


    aws_service = Column(
        String(100)
    )


    runtime = Column(
        String(100)
    )


    database_type = Column(
        String(100)
    )


    migration_status = Column(
        String(50),
        default="PLANNED"
    )


    readiness_score = Column(
        Float,
        default=0
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# =========================================================
# DEPENDENCY
# =========================================================

class Dependency(Base):

    __tablename__ = "dependencies"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    application_id = Column(
        Integer,
        nullable=False
    )


    name = Column(
        String(200),
        nullable=False
    )


    dependency_type = Column(
        String(100)
    )


    source = Column(
        String(100)
    )


    target = Column(
        String(100)
    )


    status = Column(
        String(50),
        default="PENDING"
    )


# =========================================================
# MIGRATION PLAN
# =========================================================

class MigrationPlan(Base):

    __tablename__ = "migration_plans"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    application_id = Column(
        Integer,
        nullable=False
    )


    strategy = Column(
        String(100)
    )


    priority = Column(
        String(50)
    )


    estimated_downtime = Column(
        String(100)
    )


    risk_level = Column(
        String(50)
    )


    owner = Column(
        String(200)
    )


    status = Column(
        String(50),
        default="PLANNED"
    )


    notes = Column(
        Text
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================================
# VALIDATION CHECK
# =========================================================

class ValidationCheck(Base):

    __tablename__ = "validation_checks"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    application_id = Column(
        Integer,
        nullable=False
    )


    check_name = Column(
        String(200),
        nullable=False
    )


    category = Column(
        String(100)
    )


    description = Column(
        Text
    )


    status = Column(
        String(50),
        default="PENDING"
    )


    severity = Column(
        String(50),
        default="INFO"
    )


    executed_at = Column(
        DateTime
    )


# =========================================================
# MIGRATION EVENT
# =========================================================

class MigrationEvent(Base):

    __tablename__ = "migration_events"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    application_id = Column(
        Integer,
        nullable=False
    )


    event_type = Column(
        String(100)
    )


    message = Column(
        Text
    )


    status = Column(
        String(50)
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )