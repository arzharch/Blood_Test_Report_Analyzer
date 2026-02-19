import os
from dotenv import load_dotenv
from crewai import Agent
from crewai.tools import tool
from langchain_ollama import ChatOllama


load_dotenv()

# ---------- TOOLS ----------

@tool("Analyze Blood Report for Nutrition Guidance")
def analyze_nutrition(blood_report: str) -> str:
    """Reviews blood test data and returns dietary suggestions based on identified biomarker patterns."""
    suggestions = []
    report_lower = blood_report.lower()
    
    if "cholesterol" in report_lower or "lipid" in report_lower or "triglycerides" in report_lower:
        suggestions.append("For elevated lipid markers: Reduce saturated fats and increase soluble fiber (oats, legumes, fruits).")
    
    if "hemoglobin" in report_lower or "ferritin" in report_lower or "iron" in report_lower:
        suggestions.append("For low iron markers: Prioritize iron-rich foods like spinach, lentils, or lean proteins, paired with Vitamin C for better absorption.")
    
    if "vitamin d" in report_lower or "25-hydroxy" in report_lower:
        suggestions.append("For Vitamin D concerns: Include fortified dairy, egg yolks, and fatty fish. Consider safe sun exposure.")

    if "glucose" in report_lower or "hba1c" in report_lower:
        suggestions.append("For blood sugar management: Focus on complex carbohydrates and fiber while limiting processed sugars.")

    if not suggestions:
        suggestions.append("Maintain a balanced diet with a variety of whole foods, focusing on lean proteins, vegetables, and whole grains.")

    suggestions.append("Always consult a certified nutritionist or doctor before making significant dietary changes.")
    return "\n".join(suggestions)


@tool("Generate Exercise Plan from Blood Report")
def generate_exercise_plan(blood_report: str) -> str:
    """Interprets key health indicators and offers exercise suggestions tailored to metabolic and cardiovascular status."""
    suggestions = []
    report_lower = blood_report.lower()

    if "cholesterol" in report_lower or "lipid" in report_lower:
        suggestions.append("To support lipid profiles: Engage in 150 minutes of moderate aerobic activity (brisk walking, swimming) per week.")

    if "hemoglobin" in report_lower or "iron" in report_lower:
        suggestions.append("If iron is low: Focus on low-impact movement and prioritize recovery to avoid excessive fatigue.")

    if "glucose" in report_lower or "hba1c" in report_lower:
        suggestions.append("For metabolic health: Combine aerobic exercise with twice-weekly resistance training to improve insulin sensitivity.")

    if not suggestions:
        suggestions.append("General recommendation: Aim for a mix of cardiovascular exercise and strength training most days of the week.")

    suggestions.append("Always obtain medical clearance before beginning any new fitness regimen.")
    return "\n".join(suggestions)


@tool("Verify Uploaded Blood Report")
def verify_report(blood_text: str) -> str:
    """Scans the report for signs of authenticity — looks for structured lab panels, biomarkers, and references."""
    keywords = ["Reference Range", "Result", "Units", "Lab", "Hemoglobin", "Glucose", "Patient"]
    hits = sum(1 for word in keywords if word.lower() in blood_text.lower())
    if hits >= 3:
        return "✅ Document appears to be a valid medical report with standard blood panel structure."
    return "⚠️ This may not be a typical blood report. Please ensure the uploaded file is a valid diagnostic document."


# ---------- LOCAL LLM via Ollama ----------

llm = ChatOllama(model="ollama/mistral", temperature=0.3)


# ---------- AGENTS ----------

doctor = Agent(
    role="Medical Report Analyst",
    goal="Interpret blood test results clearly and responsibly, addressing the user's specific query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a clinical analyst specializing in blood diagnostics. "
        "Your priority is to answer the patient's specific question ({query}) using the provided lab data. "
        "You explain markers clearly but never diagnose. You always recommend a physician follow-up."
    ),
    tools=[],
    llm=llm,
    allow_delegation=False
)


verifier = Agent(
    role="Medical Document Verifier",
    goal="Confirm the document is a legitimate lab report before analysis proceeds.",
    verbose=True,
    memory=False,
    backstory=(
        "You screen documents for diagnostic standards to ensure only credible reports are processed."
    ),
    tools=[verify_report],
    llm=llm,
    allow_delegation=False
)


nutritionist = Agent(
    role="Registered Nutrition Advisor",
    goal="Provide food-based guidance that specifically addresses the user's query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a dietitian who interprets blood results to answer patient questions about food and nutrition. "
        "You prioritize answering the user's specific query: '{query}' based on their lab markers."
    ),
    tools=[analyze_nutrition],
    llm=llm,
    allow_delegation=False,
    max_iter=3,
    max_rpm=10
)


exercise_specialist = Agent(
    role="Health-first Fitness Coach",
    goal="Suggest physical activities that align with the user's query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified coach who uses blood biomarkers to answer user questions about exercise and activity safety."
    ),
    tools=[generate_exercise_plan],
    llm=llm,
    allow_delegation=False,
    max_rpm=10,
    max_iter=3
)

summary_agent = Agent(
    role="Chief Health Coordinator",
    goal="Synthesize specialist insights to directly and concisely answer the user's specific question: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are the final point of contact for the patient. You take the detailed analyses from the doctor, "
        "nutritionist, and exercise specialist and distill them into a clear, direct answer to the user's "
        "original question: '{query}'. You cut through the technical jargon to provide actionable advice "
        "that specifically addresses what the user asked."
    ),
    tools=[],
    llm=llm,
    allow_delegation=False
)
