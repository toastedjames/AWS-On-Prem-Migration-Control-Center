// =========================================================
// MIGRATIONHUB
// =========================================================


// =========================================================
// RUN MIGRATION ASSESSMENT
// =========================================================

async function runAssessment(applicationId) {

    const button =
        document.querySelector(
            ".primary-button"
        );


    if (button) {

        button.disabled = true;

        button.textContent =
            "Running Assessment...";

    }


    try {

        const response =
            await fetch(
                `/api/applications/${applicationId}/assess`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Assessment failed."
            );

        }


        const result =
            await response.json();


        console.log(
            "Migration assessment:",
            result
        );


        window.location.reload();

    }


    catch (error) {

        console.error(error);


        alert(
            "Unable to complete migration assessment."
        );


        if (button) {

            button.disabled = false;

            button.textContent =
                "Run Migration Assessment";

        }

    }

}


// =========================================================
// CREATE MIGRATION PLAN
// =========================================================

async function createMigrationPlan(
    event,
    applicationId
) {

    event.preventDefault();


    const strategy =
        document.getElementById(
            "strategy"
        ).value;


    const priority =
        document.getElementById(
            "priority"
        ).value;


    const riskLevel =
        document.getElementById(
            "risk_level"
        ).value;


    const downtime =
        document.getElementById(
            "estimated_downtime"
        ).value;


    const owner =
        document.getElementById(
            "owner"
        ).value;


    const notes =
        document.getElementById(
            "notes"
        ).value;


    const button =
        event.target.querySelector(
            "button[type='submit']"
        );


    button.disabled = true;

    button.textContent =
        "Creating Plan...";


    try {

        const params =
            new URLSearchParams({

                strategy:
                    strategy,

                priority:
                    priority,

                estimated_downtime:
                    downtime,

                risk_level:
                    riskLevel,

                owner:
                    owner,

                notes:
                    notes

            });


        const response =
            await fetch(
                `/api/applications/${applicationId}/plans?${params}`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Unable to create migration plan."
            );

        }


        const result =
            await response.json();


        console.log(
            "Migration plan created:",
            result
        );


        alert(
            "Migration plan created successfully."
        );


        window.location.href =
            "/plans";

    }


    catch (error) {

        console.error(error);


        alert(
            "Unable to create migration plan."
        );


        button.disabled = false;

        button.textContent =
            "Create Migration Plan";

    }

}


// =========================================================
// RUN MIGRATION VALIDATION
// =========================================================

async function runValidation(
    applicationId,
    event
) {

    const button =
        event.currentTarget;


    button.disabled = true;

    button.textContent =
        "Validating...";


    try {

        const response =
            await fetch(
                `/api/applications/${applicationId}/validate`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Validation failed."
            );

        }


        const result =
            await response.json();


        console.log(
            "Validation result:",
            result
        );


        // -------------------------------------------------
        // PASSED
        // -------------------------------------------------

        if (
            result.overall_status === "PASSED"
        ) {

            alert(
                "Validation PASSED.\n\n" +
                `${result.passed} checks passed.`
            );

        }


        // -------------------------------------------------
        // WARNING
        // -------------------------------------------------

        else if (
            result.overall_status === "WARNING"
        ) {

            alert(
                "Validation completed with warnings.\n\n" +
                `${result.passed} passed\n` +
                `${result.warnings} warnings`
            );

        }


        // -------------------------------------------------
        // FAILED
        // -------------------------------------------------

        else {

            alert(
                "Validation FAILED.\n\n" +
                `${result.failed} checks failed.`
            );

        }


        // Refresh page after validation

        window.location.reload();

    }


    catch (error) {

        console.error(error);


        alert(
            "Unable to complete validation."
        );


        button.disabled = false;

        button.textContent =
            "Run Validation";

    }

}