from core.state import SupportState


def human_review_node(state: SupportState):

    response = state["final_response"]

    print("\n==============================")
    print("HUMAN REVIEW REQUIRED")
    print("==============================")

    print(response)

    approval = input("\nApprove response? (yes/no): ")

    if approval.lower() != "yes":
        raise Exception("Response rejected by reviewer")

    return {
        "resolved": True,
    }