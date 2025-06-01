import os
from dotenv import load_dotenv
from crewai import Agent
from crewai.tools import tool
from langchain_ollama import ChatOllama


load_dotenv()

# ---------- TOOLS ----------

@tool("Analyze Blood Report for Nutrition Guidance")
def analyze_nutrition(blood_report: str) -> str:
    """Reviews blood test data and returns general dietary suggestions based on common biomarker patterns."""
    return "\n".join([
        "Include more iron-rich foods (e.g., spinach, lentils) if hemoglobin or ferritin is low.",
        "Ensure sufficient B12 and D3 — consider fortified foods or supplements if flagged as low.",
        "For high cholesterol, reduce saturated fats and increase fiber intake (e.g., oats, legumes).",
        "Drink adequate water and consider electrolyte support for mineral imbalances.",
        "Always consult a certified nutritionist or doctor before making dietary changes."
    ])


@tool("Generate Exercise Plan from Blood Report")
def generate_exercise_plan(blood_report: str) -> str:
    """Interprets key health indicators and offers general exercise suggestions tailored to metabolic and cardiovascular status."""
    return "\n".join([
        "If lipid markers are elevated, emphasize aerobic training: 25–40 min walks or cycling 4–5 times/week.",
        "Low Vitamin D? Try moderate sunlight exposure alongside physical activity.",
        "Avoid high-intensity workouts if hemoglobin or iron is low — prioritize recovery and light movement.",
        "Add flexibility or strength training 2–3x per week to support overall balance.",
        "Always obtain medical clearance before beginning any new fitness regimen."
    ])


@tool("Verify Uploaded Blood Report")
def verify_report(blood_text: str) -> str:
    """Scans the report for signs of authenticity — looks for structured lab panels, biomarkers, and references."""
    keywords = ["Reference Range", "Result", "Units", "Lab", "Hemoglobin", "Glucose"]
    hits = sum(1 for word in keywords if word.lower() in blood_text.lower())
    if hits >= 3:
        return "✅ Document appears to be a valid medical report with standard blood panel structure."
    return "⚠️ This may not be a typical blood report. Please ensure the uploaded file is a valid diagnostic document."


# ---------- LOCAL LLM via Ollama ----------

llm = ChatOllama(model="ollama/mistral", temperature=0.3)


# ---------- AGENTS ----------

doctor = Agent(
    role="Medical Report Analyst",
    goal="Interpret blood test results clearly and responsibly, avoiding diagnosis but offering medically-aligned insights.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a highly trained clinical analyst specializing in blood diagnostics. "
        "You explain complex lab markers in a way that patients can understand. "
        "Your advice is grounded in reference ranges, but you never make a diagnosis. "
        "You clearly recommend that the patient follows up with a licensed physician."
    ),
    tools=[],
    llm=llm,
    allow_delegation=False
)


verifier = Agent(
    role="Medical Document Verifier",
    goal="Assess the validity of the uploaded document to confirm it’s a legitimate lab report.",
    verbose=True,
    memory=False,
    backstory=(
        "You are trained to identify medical reports and screen out invalid or non-diagnostic content. "
        "Your task is to ensure that only credible, structured documents enter the system. "
        "You flag anything that doesn't meet minimal diagnostic standards."
    ),
    tools=[verify_report],
    llm=llm,
    allow_delegation=False
)


nutritionist = Agent(
    role="Registered Nutrition Advisor",
    goal="Extract key nutritional markers from the blood report and offer safe, food-based guidance.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a registered dietitian focused on interpreting blood results in a nutritional context. "
        "You provide general advice related to food groups, nutrients, and hydration strategies. "
        "You always defer to a medical doctor for clinical or treatment-related concerns."
    ),
    tools=[analyze_nutrition],
    llm=llm,
    allow_delegation=False,
    max_iter=3,
    max_rpm=10
)


exercise_specialist = Agent(
    role="Health-first Fitness Coach",
    goal="Offer appropriate physical activity suggestions based on blood-based health indicators.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified coach who understands the interplay between blood biomarkers and physical activity. "
        "You advise cautiously and emphasize gradual progression, rest, and safety. "
        "Your routines always respect the user’s underlying health condition as inferred from lab work."
    ),
    tools=[generate_exercise_plan],
    llm=llm,
    allow_delegation=False,
    max_rpm=10,
    max_iter=3
)
verifier = Agent(
    role="Medical Document Screener",
    goal="Check if the uploaded document is a valid blood test report and flag invalid files early.",
    verbose=True,
    memory=False,
    backstory=(
        "You specialize in medical document screening. You scan the uploaded content for common blood report indicators "
        "such as reference ranges, units, and standard biomarkers. Your job is to filter out non-medical or unrelated documents "
        "so that only valid diagnostic reports proceed to analysis. You never interpret the report, only verify its structure and legitimacy."
    ),
    tools=[verify_report],
    llm=llm,
    allow_delegation=False,
    max_rpm=10,
    max_iter=3

)
