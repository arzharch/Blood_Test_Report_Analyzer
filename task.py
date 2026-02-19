from crewai import Task
from agents import doctor, nutritionist, exercise_specialist, analyze_nutrition, generate_exercise_plan
from agents import verifier, verify_report, summary_agent

# Verification task
verification_task = Task(
    description=(
        "Review the uploaded document content ({blood_text}) and determine if it appears to be a valid blood test report. "
        "Focus on identifying typical elements such as medical terminology, standard lab values, units, or reference ranges."
    ),
    expected_output=(
        "A short verification message indicating whether the document seems to be a valid diagnostic blood report or not. "
        "If not, clearly explain what’s missing (e.g., no biomarkers, missing lab structure, etc.)."
    ),
    agent=verifier,
    tools=[verify_report],
    input_vars=["query", "blood_text"],
    async_execution=False
)

# Doctor task
help_patients = Task(
    description=(
        "Review the user's blood test report and summarize any abnormalities, "
        "notable lab values, and provide high-level medical recommendations based on the report text: {blood_text}."
    ),
    expected_output=(
        "A summary of the blood test report with any potential concerns, "
        "normal or abnormal values, and clear next-step recommendations. "
        "Include suggestions for speaking with a healthcare provider."
    ),
    agent=doctor,
    tools=[], 
    input_vars=["query", "blood_text"],
    async_execution=False
)

# Nutrition analysis task
nutrition_analysis = Task(
    description=(
        "Analyze the provided blood test report text ({blood_text}) AND specifically address the user's query: '{query}'. "
        "Identify any dietary deficiencies, imbalances, or optimizations relevant to the report and the query. "
        "Provide evidence-based nutrition advice in layman's terms."
    ),
    expected_output=(
        "A personalized nutrition recommendation list that directly answers the user's query based on the blood report. "
        "Include nutrient focus areas, food types to prioritize (or avoid if asked), and possible supplements if relevant."
    ),
    agent=nutritionist,
    tools=[analyze_nutrition],
    input_vars=["query", "blood_text"],
    async_execution=False
)

# Exercise planning task
exercise_planning = Task(
    description=(
        "Based on the blood test report ({blood_text}) and the user's specific query: '{query}', "
        "generate a health-appropriate exercise plan. Factor in cardiovascular fitness, metabolic state, or any abnormalities "
        "mentioned in the report that are relevant to the user's question."
    ),
    expected_output=(
        "An exercise plan tailored to the user's condition and query, including suggested frequency, types of exercise, "
        "and any relevant safety precautions or goals."
    ),
    agent=exercise_specialist,
    tools=[generate_exercise_plan],
    input_vars=["query", "blood_text"],
    async_execution=False
)

# Final Specific Answer Task
specific_query_answer = Task(
    description=(
        "You have access to the doctor's analysis, the nutritionist's advice, and the exercise specialist's plan. "
        "Your final task is to answer the user's specific query: '{query}' as directly and concisely as possible. "
        "Do not repeat all the technical details, but synthesize them into a clear answer for the user."
    ),
    expected_output=(
        "A clear, direct answer to the user's query: '{query}', synthesizing information from all previous tasks."
    ),
    agent=summary_agent,
    tools=[],
    input_vars=["query", "blood_text"],
    async_execution=False
)
