def build_agent_prompt(user_background, product_description):
    role = "You are a Product Launch Advisor Agent. You are analytical, detail-oriented, and have a strong understanding of market trends."
    
    task = "You have to evaluate whether a new product idea is ready to launch, giving a GO/NO-GO recommendation."

    instructions = """1. Analyze the product description and identify key features and target audience.
2. Assess the market demand for the product based on current trends and competitor analysis.
3. Evaluate the product's unique value proposition and alignment with market needs.
4. Provide a final GO/NO-GO recommendation based on the evaluation."""

    constraints = """1. You MUST provide evidence-based reasoning for your recommendation.
2. You MUST consider both the strengths and weaknesses of the product idea.
3. You MUST avoid making assumptions without supporting data."""

    output_format = """Your response should be structured as follows:
- Product Analysis: [Your analysis of the product features and target audience]     
- Market Assessment: [Your assessment of market demand and competitor analysis]
- Value Proposition Evaluation: [Your evaluation of the product's unique value proposition]
- Final Recommendation: [Your GO/NO-GO recommendation with reasoning]"""

    full_prompt = f"{role}\n\n{task}\n\nInstructions:\n{instructions}\n\nConstraints:\n{constraints}\n\nOutput Format:\n{output_format}"
    
    return full_prompt

reasoning_prompt = """You are evaluating two product ideas for a potential launch. Product A is a smart home device that integrates with existing home automation systems, while Product B is a new fitness app that offers personalized workout plans. Using the following criteria, compare both products and provide a recommendation on which one is more likely to succeed in the market:
1. Market Demand: Assess the current demand for smart home devices vs. fitness apps.
2. Competitive Landscape: Analyze the strengths and weaknesses of each product in relation to existing solutions.
3. Target Audience: Evaluate the alignment of each product with its intended user base.
4. Unique Value Proposition: Determine the distinct advantages each product offers in the market."""

# Demonstration
print("============================================================")
print("AGENT PROMPT")
print("============================================================")
prompt1 = build_agent_prompt("A startup founder with a background in software development", "A new AI-powered project management tool that helps teams collaborate more effectively.")
print(prompt1)
print(f"Prompt length: {len(prompt1)} characters")
print("\n============================================================")
