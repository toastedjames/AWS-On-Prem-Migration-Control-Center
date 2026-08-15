from fastapi import (
    FastAPI,
    Request,
    Depends
)

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import (
    Base,
    engine,
    get_db
)

from models import (
    Application,
    Dependency,
    MigrationPlan,
    ValidationCheck,
    MigrationEvent
)

from migration import create_default_applications


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="MigrationHub",
    description=(
        "AWS-to-On-Prem Application "
        "Migration Control Center"
    ),
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)

# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(
    bind=engine
)


create_default_applications()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():

    return {

        "application":
            "MigrationHub",

        "status":
            "UP",

        "version":
            "1.0.0"

    }

# =========================================================
# API — MIGRATION ASSESSMENT
# =========================================================

@app.post(
    "/api/applications/{application_id}/assess"
)
def assess_application_api(
    application_id: int
):

    from migration import assess_application

    return assess_application(
        application_id
    )

# =========================================================
# DASHBOARD
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    applications = (
        db.query(Application)
        .order_by(
            Application.name
        )
        .all()
    )


    total_applications = (
        db.query(Application)
        .count()
    )


    ready_applications = (
        db.query(Application)
        .filter(
            Application.migration_status == "READY"
        )
        .count()
    )


    assessment_applications = (
        db.query(Application)
        .filter(
            Application.migration_status == "ASSESSMENT"
        )
        .count()
    )


    migrated_applications = (
        db.query(Application)
        .filter(
            Application.migration_status == "COMPLETED"
        )
        .count()
    )


    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={

            "applications":
                applications,

            "total_applications":
                total_applications,

            "ready_applications":
                ready_applications,

            "assessment_applications":
                assessment_applications,

            "migrated_applications":
                migrated_applications
        }
    )

# =========================================================
# APPLICATION INVENTORY
# =========================================================

@app.get(
    "/applications",
    response_class=HTMLResponse
)
def applications_page(
    request: Request,
    db: Session = Depends(get_db)
):

    applications = (
        db.query(Application)
        .order_by(
            Application.name
        )
        .all()
    )


    return templates.TemplateResponse(
        request=request,
        name="applications.html",
        context={
            "applications":
                applications
        }
    )

# =========================================================
# APPLICATION DETAILS
# =========================================================

@app.get(
    "/applications/{application_id}",
    response_class=HTMLResponse
)
def application_detail(
    application_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )


    if not application:

        return HTMLResponse(
            content="Application not found",
            status_code=404
        )


    dependencies = (
        db.query(Dependency)
        .filter(
            Dependency.application_id
            == application_id
        )
        .all()
    )


    plans = (
        db.query(MigrationPlan)
        .filter(
            MigrationPlan.application_id
            == application_id
        )
        .all()
    )


    validations = (
        db.query(ValidationCheck)
        .filter(
            ValidationCheck.application_id
            == application_id
        )
        .all()
    )


    events = (
        db.query(MigrationEvent)
        .filter(
            MigrationEvent.application_id
            == application_id
        )
        .order_by(
            desc(MigrationEvent.created_at)
        )
        .limit(10)
        .all()
    )


    return templates.TemplateResponse(
        request=request,
        name="application_detail.html",
        context={

            "application":
                application,

            "dependencies":
                dependencies,

            "plans":
                plans,

            "validations":
                validations,

            "events":
                events
        }
    )

# =========================================================
# MIGRATION PLAN — CREATE
# =========================================================

@app.post(
    "/api/applications/{application_id}/plans"
)
def create_migration_plan(
    application_id: int,
    strategy: str,
    priority: str,
    estimated_downtime: str,
    risk_level: str,
    owner: str,
    notes: str = "",
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if not application:

        return {
            "error":
                "Application not found"
        }


    plan = MigrationPlan(

        application_id =
            application_id,

        strategy =
            strategy,

        priority =
            priority,

        estimated_downtime =
            estimated_downtime,

        risk_level =
            risk_level,

        owner =
            owner,

        status =
            "PLANNED",

        notes =
            notes
    )


    db.add(plan)

    db.commit()

    db.refresh(plan)


    # Record migration activity

    event = MigrationEvent(

        application_id =
            application_id,

        event_type =
            "MIGRATION_PLAN_CREATED",

        message =
            (
                f"Migration plan created using "
                f"{strategy} strategy. "
                f"Priority: {priority}. "
                f"Risk: {risk_level}."
            ),

        status =
            "PLANNED"
    )


    db.add(event)

    db.commit()


    return {

        "message":
            "Migration plan created successfully",

        "plan_id":
            plan.id,

        "application_id":
            plan.application_id,

        "strategy":
            plan.strategy,

        "priority":
            plan.priority,

        "risk_level":
            plan.risk_level,

        "status":
            plan.status
    }

# =========================================================
# MIGRATION PLANS PAGE
# =========================================================

@app.get(
    "/plans",
    response_class=HTMLResponse
)
def migration_plans_page(
    request: Request,
    db: Session = Depends(get_db)
):

    plans = (
        db.query(MigrationPlan)
        .order_by(
            desc(MigrationPlan.created_at)
        )
        .all()
    )


    applications = (
        db.query(Application)
        .order_by(
            Application.name
        )
        .all()
    )


    return templates.TemplateResponse(
        request=request,
        name="plans.html",
        context={

            "plans":
                plans,

            "applications":
                applications

        }
    )

# =========================================================
# API — MIGRATION VALIDATION
# =========================================================

@app.post(
    "/api/applications/{application_id}/validate"
)
def validate_application_api(
    application_id: int
):

    from migration import validate_application

    return validate_application(
        application_id
    )

# =========================================================
# VALIDATION PAGE
# =========================================================

@app.get(
    "/validation",
    response_class=HTMLResponse
)
def validation_page(
    request: Request,
    db: Session = Depends(get_db)
):

    applications = (
        db.query(Application)
        .order_by(
            Application.name
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="validation.html",
        context={
            "applications":
                applications
        }
    )

# =========================================================
# REPORTS PAGE
# =========================================================

@app.get(
    "/reports",
    response_class=HTMLResponse
)
def reports_page(
    request: Request,
    db: Session = Depends(get_db)
):

    applications = (
        db.query(Application)
        .order_by(Application.name)
        .all()
    )

    plans = (
        db.query(MigrationPlan)
        .order_by(
            desc(MigrationPlan.created_at)
        )
        .all()
    )

    validations = (
        db.query(ValidationCheck)
        .order_by(
            desc(ValidationCheck.executed_at)
        )
        .all()
    )

    events = (
        db.query(MigrationEvent)
        .order_by(
            desc(MigrationEvent.created_at)
        )
        .limit(15)
        .all()
    )


    # -----------------------------------------------------
    # Application statistics
    # -----------------------------------------------------

    total_applications = len(applications)

    ready_count = sum(
        application.migration_status == "READY"
        for application in applications
    )

    assessment_count = sum(
        application.migration_status == "ASSESSMENT"
        for application in applications
    )

    review_count = sum(
        application.migration_status == "REVIEW_REQUIRED"
        for application in applications
    )

    completed_count = sum(
        application.migration_status == "COMPLETED"
        for application in applications
    )


    # -----------------------------------------------------
    # Average readiness
    # -----------------------------------------------------

    if applications:

        average_readiness = (
            sum(
                application.readiness_score or 0
                for application in applications
            )
            / total_applications
        )

    else:

        average_readiness = 0


    # -----------------------------------------------------
    # Strategy statistics
    # -----------------------------------------------------

    strategy_counts = {

        "REHOST":
            sum(
                plan.strategy == "REHOST"
                for plan in plans
            ),

        "REPLATFORM":
            sum(
                plan.strategy == "REPLATFORM"
                for plan in plans
            ),

        "REFACTOR":
            sum(
                plan.strategy == "REFACTOR"
                for plan in plans
            )
    }


    # -----------------------------------------------------
    # Risk statistics
    # -----------------------------------------------------

    risk_counts = {

        "LOW":
            sum(
                plan.risk_level == "LOW"
                for plan in plans
            ),

        "MEDIUM":
            sum(
                plan.risk_level == "MEDIUM"
                for plan in plans
            ),

        "HIGH":
            sum(
                plan.risk_level == "HIGH"
                for plan in plans
            )
    }


    # -----------------------------------------------------
    # Validation statistics
    # -----------------------------------------------------

    validation_passed = sum(
        check.status == "PASS"
        for check in validations
    )

    validation_failed = sum(
        check.status == "FAIL"
        for check in validations
    )

    validation_warnings = sum(
        check.status == "WARNING"
        for check in validations
    )


    return templates.TemplateResponse(

        request=request,

        name="reports.html",

        context={

            "applications":
                applications,

            "plans":
                plans,

            "validations":
                validations,

            "events":
                events,

            "total_applications":
                total_applications,

            "ready_count":
                ready_count,

            "assessment_count":
                assessment_count,

            "review_count":
                review_count,

            "completed_count":
                completed_count,

            "average_readiness":
                average_readiness,

            "strategy_counts":
                strategy_counts,

            "risk_counts":
                risk_counts,

            "validation_passed":
                validation_passed,

            "validation_failed":
                validation_failed,

            "validation_warnings":
                validation_warnings
        }
    )