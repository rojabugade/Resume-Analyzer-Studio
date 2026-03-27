from pprint import pprint

from resume_analyzer.agents.langgraph_flow import resume_workflow_graph

if __name__ == "__main__":
    resume_text = """
    Senior Software Engineer
    Professional Summary: Backend engineer with 6 years building APIs in Python and AWS.
    Skills: Python, FastAPI, AWS, Docker, SQL
    Experience: Led API modernization and mentoring for a 6-person team.
    """

    result = resume_workflow_graph.invoke(
        {
            "session_id": "demo-session",
            "user_id": "candidate_001",
            "query": "Find matching jobs and optimize my resume",
            "resume_text": resume_text,
        }
    )

    print("=== Resume Analyzer Sample Run ===")
    pprint(result)
