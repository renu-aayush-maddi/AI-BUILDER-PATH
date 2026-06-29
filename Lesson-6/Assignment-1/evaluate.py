import time
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from agentevals.trajectory.match import create_trajectory_match_evaluator
from agentevals.trajectory.llm import create_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE

from main import support_app 

load_dotenv()

def run_agentevals():
    print("Starting AgentEvals Benchmark...\n")

    # 1. Define the Evaluation Dataset
    dataset = [
        {
            "input": "How do I set up my VPN?",
            "expected_tool": "read_document", 
            "expected_tool_args": {"department": "IT", "filename": "vpn_setup.txt"},
            "expected_response": "To set up your VPN, follow these steps..."
        },
        {
            "input": "What is the capital of India?",
            "expected_tool": None,
            "expected_tool_args": None,
            "expected_response": "Blocked by Policy: I am a corporate support assistant and can only assist with IT and Finance policies."
        }
    ]

    # 2. Initialize AgentEvals Evaluators
    
    tool_evaluator = create_trajectory_match_evaluator(trajectory_match_mode="superset")
    
    # NEW: We are using the WITH_REFERENCE prompt so the judge knows "Blocked by Policy" is the correct answer
    llm_judge = create_trajectory_llm_as_judge(
        model="openai:gpt-4o", 
        prompt=TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE
    )

    results = []

    # 3. Run the Benchmark Loop
    for i, data in enumerate(dataset):
        print(f"--- Running Test {i+1}: '{data['input']}' ---")
        
        start_time = time.time()
        
        run_config = {"configurable": {"thread_id": f"eval_test_{i}"}}
        final_state = support_app.invoke(
            {"messages": [HumanMessage(content=data["input"])]}, 
            config=run_config
        )
        
        latency = round(time.time() - start_time, 2)
        output_messages = final_state["messages"]

        # --- Build Reference Trajectories ---
        if data["expected_tool"]:
            # Valid IT/Finance Query Reference
            reference_trajectory = [
                HumanMessage(content=data["input"]),
                AIMessage(content="", tool_calls=[
                    {"id": "mock_1", "name": data["expected_tool"], "args": data["expected_tool_args"]}
                ]),
                AIMessage(content=data["expected_response"])
            ]
            
            tool_evaluation = tool_evaluator(
                outputs=output_messages, 
                reference_outputs=reference_trajectory
            )
            tool_success = tool_evaluation["score"]
        else:
            # Blocked Guardrail Query Reference
            reference_trajectory = [
                HumanMessage(content=data["input"]),
                AIMessage(content=data["expected_response"])
            ]
            
            tool_calls_made = any(hasattr(msg, 'tool_calls') and msg.tool_calls for msg in output_messages)
            tool_success = not tool_calls_made

        # Evaluate Correctness & Hallucinations with Reference
        quality_evaluation = llm_judge(
            outputs=output_messages,
            reference_outputs=reference_trajectory  # Passing the reference here!
        )
        quality_score = quality_evaluation["score"]

        print(f"Latency: {latency}s")
        print(f"Trajectory Quality (Correctness/No Hallucinations): {quality_score}")
        print(f"Tool Usage Match: {tool_success}\n")

        results.append({
            "latency": latency,
            "quality": 1 if quality_score else 0,
            "tool_success": 1 if tool_success else 0
        })

    # 4. Calculate Final Aggregate Metrics
    avg_latency = sum(r["latency"] for r in results) / len(results)
    avg_quality = (sum(r["quality"] for r in results) / len(results)) * 100
    tool_success_rate = (sum(r["tool_success"] for r in results) / len(results)) * 100

    print("====================================")
    print("      FINAL BENCHMARK RESULTS       ")
    print("====================================")
    print(f"Average Latency:        {avg_latency:.2f}s")
    print(f"Trajectory Quality:     {avg_quality}%")
    print(f"Tool Usage Match:       {tool_success_rate}%")
    print("====================================")

if __name__ == "__main__":
    run_agentevals()