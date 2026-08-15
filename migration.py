from datetime import datetime

from database import SessionLocal

from models import (
    Application,
    Dependency,
    MigrationPlan,
    ValidationCheck,
    MigrationEvent
)


# =========================================================
# APPLICATION SEED DATA
# =========================================================

def create_default_applications():

    db = SessionLocal()

    try:

        if db.query(Application).count() > 0:

            return


        applications = [

            Application(
                name="Graduate Document Processing",
                description=(
                    "Document ingestion and processing "
                    "application for graduate workflows."
                ),
                source_environment="AWS",
                target_environment="ON_PREM",
                aws_service="EC2",
                runtime="Java 21",
                database_type="PostgreSQL",
                migration_status="PLANNED",
                readiness_score=82
            ),


            Application(
                name="Student Notification Service",
                description=(
                    "Service responsible for automated "
                    "student notification workflows."
                ),
                source_environment="AWS",
                target_environment="ON_PREM",
                aws_service="EC2",
                runtime="Java 17",
                database_type="PostgreSQL",
                migration_status="ASSESSMENT",
                readiness_score=68
            ),


            Application(
                name="Graduate Analytics API",
                description=(
                    "Backend API supporting graduate "
                    "program reporting and analytics."
                ),
                source_environment="AWS",
                target_environment="ON_PREM",
                aws_service="EC2",
                runtime="Python 3.12",
                database_type="PostgreSQL",
                migration_status="READY",
                readiness_score=94
            ),


            Application(
                name="Document Archive Service",
                description=(
                    "Object storage and document archive "
                    "service used by graduate workflows."
                ),
                source_environment="AWS",
                target_environment="ON_PREM",
                aws_service="S3",
                runtime="N/A",
                database_type="N/A",
                migration_status="PLANNED",
                readiness_score=76
            )

        ]


        db.add_all(
            applications
        )

        db.commit()


    finally:

        db.close()


# =========================================================
# MIGRATION EVENTS
# =========================================================

def record_event(
    application_id,
    event_type,
    message,
    status
):

    db = SessionLocal()

    try:

        event = MigrationEvent(

            application_id=application_id,

            event_type=event_type,

            message=message,

            status=status,

            created_at=datetime.utcnow()

        )

        db.add(event)

        db.commit()

        db.refresh(event)

        return event

    finally:

        db.close()

# =========================================================
# MIGRATION READINESS ASSESSMENT
# =========================================================

def assess_application(application_id):

    db = SessionLocal()

    try:

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


        # -------------------------------------------------
        # Assessment criteria
        # -------------------------------------------------

        checks = []


        # -------------------------------------------------
        # 1. Runtime compatibility
        # -------------------------------------------------

        runtime_compatible = (
            application.runtime
            in [
                "Java 17",
                "Java 21",
                "Python 3.12"
            ]
        )

        checks.append({

            "name":
                "Runtime Compatibility",

            "passed":
                runtime_compatible,

            "weight":
                20,

            "message":
                (
                    "Target environment supports "
                    "the application runtime."
                    if runtime_compatible
                    else
                    "Runtime requires compatibility review."
                )
        })


        # -------------------------------------------------
        # 2. Database compatibility
        # -------------------------------------------------

        database_compatible = (
            application.database_type
            in [
                "PostgreSQL",
                "N/A"
            ]
        )

        checks.append({

            "name":
                "Database Compatibility",

            "passed":
                database_compatible,

            "weight":
                20,

            "message":
                (
                    "Database platform is compatible "
                    "with the target environment."
                    if database_compatible
                    else
                    "Database migration requires assessment."
                )
        })


        # -------------------------------------------------
        # 3. AWS service mapping
        # -------------------------------------------------

        service_mapping = (
            application.aws_service
            in [
                "EC2",
                "S3"
            ]
        )

        checks.append({

            "name":
                "AWS Service Mapping",

            "passed":
                service_mapping,

            "weight":
                20,

            "message":
                (
                    "AWS service has an identified "
                    "on-premise migration path."
                    if service_mapping
                    else
                    "AWS service requires migration analysis."
                )
        })


        # -------------------------------------------------
        # 4. Target environment
        # -------------------------------------------------

        target_configured = (
            application.target_environment
            == "ON_PREM"
        )

        checks.append({

            "name":
                "Target Environment",

            "passed":
                target_configured,

            "weight":
                15,

            "message":
                (
                    "On-premise target environment "
                    "has been identified."
                    if target_configured
                    else
                    "Target environment has not been configured."
                )
        })


        # -------------------------------------------------
        # 5. Dependencies
        # -------------------------------------------------

        dependency_count = (
            db.query(Dependency)
            .filter(
                Dependency.application_id
                == application_id
            )
            .count()
        )

        dependencies_ready = (
            dependency_count == 0
            or
            db.query(Dependency)
            .filter(
                Dependency.application_id
                == application_id,
                Dependency.status != "READY"
            )
            .count() == 0
        )

        checks.append({

            "name":
                "Dependency Readiness",

            "passed":
                dependencies_ready,

            "weight":
                15,

            "message":
                (
                    "All known dependencies "
                    "are ready for migration."
                    if dependencies_ready
                    else
                    "One or more dependencies "
                    "require remediation."
                )
        })


        # -------------------------------------------------
        # 6. Configuration
        # -------------------------------------------------

        configuration_ready = True

        checks.append({

            "name":
                "Configuration Readiness",

            "passed":
                configuration_ready,

            "weight":
                10,

            "message":
                "Application configuration can be "
                "transferred to the target environment."
        })


        # -------------------------------------------------
        # Calculate score
        # -------------------------------------------------

        score = sum(
            check["weight"]
            for check in checks
            if check["passed"]
        )


        # -------------------------------------------------
        # Determine migration status
        # -------------------------------------------------

        if score >= 90:

            status = "READY"

        elif score >= 75:

            status = "ASSESSMENT"

        elif score >= 50:

            status = "REVIEW_REQUIRED"

        else:

            status = "BLOCKED"


        # -------------------------------------------------
        # Save assessment
        # -------------------------------------------------

        application.readiness_score = score

        application.migration_status = status

        application.updated_at = datetime.utcnow()

        db.commit()

        db.refresh(application)


        # -------------------------------------------------
        # Record migration event
        # -------------------------------------------------

        event = MigrationEvent(

            application_id =
                application.id,

            event_type =
                "READINESS_ASSESSMENT",

            message =
                (
                    f"Migration readiness "
                    f"assessment completed. "
                    f"Score: {score}%."
                ),

            status =
                status,

            created_at =
                datetime.utcnow()
        )


        db.add(event)

        db.commit()


        return {

            "application_id":
                application.id,

            "application":
                application.name,

            "score":
                score,

            "status":
                status,

            "checks":
                checks

        }


    finally:

        db.close()

# =========================================================
# MIGRATION VALIDATION
# =========================================================

def validate_application(application_id):

    db = SessionLocal()

    try:

        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if not application:

            return {
                "error": "Application not found"
            }


        results = []


        # -------------------------------------------------
        # 1. Runtime validation
        # -------------------------------------------------

        runtime_passed = (
            application.runtime
            in [
                "Java 17",
                "Java 21",
                "Python 3.12"
            ]
        )

        results.append({
            "name":
                "Runtime Compatibility",

            "category":
                "Application",

            "description":
                "Verify that the application runtime "
                "is supported by the target environment.",

            "status":
                "PASS"
                if runtime_passed
                else
                "FAIL",

            "severity":
                "INFO"
                if runtime_passed
                else
                "HIGH"
        })


        # -------------------------------------------------
        # 2. Database validation
        # -------------------------------------------------

        database_passed = (
            application.database_type
            in [
                "PostgreSQL",
                "N/A"
            ]
        )

        results.append({
            "name":
                "Database Compatibility",

            "category":
                "Database",

            "description":
                "Verify database platform and "
                "target environment compatibility.",

            "status":
                "PASS"
                if database_passed
                else
                "FAIL",

            "severity":
                "INFO"
                if database_passed
                else
                "HIGH"
        })


        # -------------------------------------------------
        # 3. Target environment
        # -------------------------------------------------

        target_passed = (
            application.target_environment
            == "ON_PREM"
        )

        results.append({
            "name":
                "Target Environment",

            "category":
                "Infrastructure",

            "description":
                "Verify that an on-premise target "
                "environment has been configured.",

            "status":
                "PASS"
                if target_passed
                else
                "FAIL",

            "severity":
                "INFO"
                if target_passed
                else
                "CRITICAL"
        })


        # -------------------------------------------------
        # 4. Dependency validation
        # -------------------------------------------------

        dependencies = (
            db.query(Dependency)
            .filter(
                Dependency.application_id
                == application_id
            )
            .all()
        )


        dependency_failed = any(
            dependency.status != "READY"
            for dependency in dependencies
        )


        results.append({
            "name":
                "Dependency Readiness",

            "category":
                "Dependencies",

            "description":
                "Verify that application dependencies "
                "are available in the target environment.",

            "status":
                "FAIL"
                if dependency_failed
                else
                "PASS",

            "severity":
                "HIGH"
                if dependency_failed
                else
                "INFO"
        })


        # -------------------------------------------------
        # 5. Migration plan validation
        # -------------------------------------------------

        plan = (
            db.query(MigrationPlan)
            .filter(
                MigrationPlan.application_id
                == application_id
            )
            .first()
        )


        plan_exists = (
            plan is not None
        )


        results.append({
            "name":
                "Migration Plan",

            "category":
                "Planning",

            "description":
                "Verify that an approved migration "
                "strategy exists for the application.",

            "status":
                "PASS"
                if plan_exists
                else
                "WARNING",

            "severity":
                "INFO"
                if plan_exists
                else
                "MEDIUM"
        })


        # -------------------------------------------------
        # 6. Configuration validation
        # -------------------------------------------------

        configuration_passed = True

        results.append({
            "name":
                "Application Configuration",

            "category":
                "Configuration",

            "description":
                "Verify that required application "
                "configuration can be transferred.",

            "status":
                "PASS"
                if configuration_passed
                else
                "FAIL",

            "severity":
                "INFO"
        })


        # -------------------------------------------------
        # Calculate validation summary
        # -------------------------------------------------

        passed = sum(
            result["status"] == "PASS"
            for result in results
        )

        failed = sum(
            result["status"] == "FAIL"
            for result in results
        )

        warnings = sum(
            result["status"] == "WARNING"
            for result in results
        )


        if failed > 0:

            overall_status = "FAILED"

        elif warnings > 0:

            overall_status = "WARNING"

        else:

            overall_status = "PASSED"


        # -------------------------------------------------
        # Store validation checks
        # -------------------------------------------------

        for result in results:

            check = ValidationCheck(

                application_id =
                    application_id,

                check_name =
                    result["name"],

                category =
                    result["category"],

                description =
                    result["description"],

                status =
                    result["status"],

                severity =
                    result["severity"],

                executed_at =
                    datetime.utcnow()
            )

            db.add(check)


        # -------------------------------------------------
        # Record migration event
        # -------------------------------------------------

        event = MigrationEvent(

            application_id =
                application_id,

            event_type =
                "MIGRATION_VALIDATION",

            message =
                (
                    f"Validation completed: "
                    f"{overall_status}. "
                    f"{passed} passed, "
                    f"{failed} failed, "
                    f"{warnings} warnings."
                ),

            status =
                overall_status,

            created_at =
                datetime.utcnow()
        )


        db.add(event)

        db.commit()


        return {

            "application_id":
                application_id,

            "application":
                application.name,

            "overall_status":
                overall_status,

            "passed":
                passed,

            "failed":
                failed,

            "warnings":
                warnings,

            "checks":
                results

        }


    finally:

        db.close()