# Prove the skeleton works with a dummy CT cancellation scenario.
from graph import app
from agents import ComplianceState

def main():
    # Dummy CT policy that violates 30-day notice
    initial_state: ComplianceState = {
    "intent": "cancellation_compliance",
    "policy_data": {
        "policy_number": "CT-123"
    },
    "retrieved_rules": [],
    "violations": [],
    "reasoning": [],
    "violation_scores": [],
    "compliance_score": 0.0,
    "requires_escalation": False,
    "final_response": ""
}

    result = app.invoke(initial_state)
    print("Final response:", result["final_response"])
    print("Compliance score:", result["compliance_score"])
    print("Violations:", result["violations"])

if __name__ == "__main__":
    main()
