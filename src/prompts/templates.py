"""
Prompt Templates:
"""

QUERY_TRANSFORM_PROMPT = """You are a research query optimizer. Transform the user's query into a clear, research-oriented question.
User Query: {user_query}

Your task:
1. Clarify any vague or ambiguous terms
2. Add research-oriented framing (analyze, evaluate, examine, compare)
3. Ensure the query is specific enough for academic/industry research
4. Identify the core research focus

Respond in this format:
Transformed: [Your improved research query here]
Focus: [Main research focus in 2-3 words]

Rules:
- Keep the original intent intact
- Make it suitable for finding academic papers and industry reports
- If the query is about a technology/concept, frame it to explore both benefits and challenges
- Keep it concise but comprehensive (1-2 sentences max)

Example:
User Query: "AI bad for jobs?"
Transformed: What are the economic and social impacts of artificial intelligence on employment, including both job displacement risks and new opportunities created?
Focus: economic impact analysis"""

PLANNING_PROMPT = """You are a research planning expert. Create a comprehensive research plan for the following topic:

Research Topic: {research_topic}

Generate a research plan that includes:

1. Research Angles (3-5 different perspectives to investigate)
2. Search Queries (5-8 specific queries to find relevant information)
3. Focus Areas (key aspects that must be covered)

Format your response as JSON:
{{
    "research_angles": ["angle1", "angle2", ...],
    "search_queries": ["query1", "query2", ...],
    "focus_areas": ["area1", "area2", ...]
}}

Be specific and ensure queries will find both academic and industry sources."""

RELEVANCY_CHECK_PROMPT = """You are a research quality validator. Analyze whether the research plan aligns with the user's original intent.

Original User Query: {original_query}
Transformed Query: {transformed_query}

Research Plan:
- Research Angles: {research_angles}
- Search Queries: {search_queries}
- Focus Areas: {focus_areas}

Your task:
1. Determine if the research plan addresses the original user query
2. Check if the research angles match the user's intent
3. Verify that search queries would find relevant information
4. Assess overall relevancy (score 0.0 to 1.0)

Respond in this format:
Relevancy Score: [0.0-1.0]
Is Relevant: [Yes/No]
Reasoning: [Brief explanation of why the plan is or isn't relevant]

Threshold: If score < 0.6, mark as "Not Relevant"

Be strict - if the plan seems generic, off-topic, or doesn't address the core question, mark it as not relevant."""

DIRECT_ANSWER_PROMPT = """The user asked: {original_query}

The transformed query was: {transformed_query}

However, the automated research planning process determined that it could not create a sufficiently relevant research plan. The issue was: {relevancy_issue}

Provide a comprehensive, well-structured answer to the original user query based on your knowledge. Be clear that this is based on general knowledge rather than current research.

Format your response as a clear, informative answer that:
1. Directly addresses the user's question
2. Provides relevant information and context
3. Acknowledges limitations where appropriate
4. Uses clear structure with headers if needed

Be helpful and informative, but also transparent about the limitations of this approach."""

EXTRACTION_PROMPT = """Extract relevant evidence from the following content:

Title: {title}
Content: {content}

Research Context: {context}
Focus Areas: {focus_areas}

Extract and summarize:
1. Key claims or findings
2. Supporting data or statistics
3. Relevant quotes or insights
4. Any mentioned risks or benefits
5. Evaluation methods or quality measures discussed

Be concise but comprehensive. Separate facts from opinions."""

SYNTHESIS_PROMPT = """Create a comprehensive research report based on the following evidence:

Research Topic: {research_topic}
Research Angles: {research_angles}
Focus Areas: {focus_areas}

Evidence:
{evidence}

Write a well-structured Markdown report that:

1. Starts with an executive summary
2. Identifies multiple research angles as found in the evidence
3. Separates claims from supporting evidence
4. Addresses each focus area
5. Maintains academic objectivity
6. Highlights both risks and benefits where applicable
7. Discusses data quality, bias, and evaluation methods if mentioned
8. Provides clear conclusions

Use proper Markdown formatting with headers, bullet points, and emphasis where appropriate.
Focus on synthesizing information rather than just listing it."""
