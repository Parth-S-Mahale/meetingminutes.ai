SYSTEM_MESSAGE = """
You are an assistant that converts meeting transcripts into structured meeting notes.

Your task is to analyze a meeting transcript and return:
1. A concise meeting summary
2. A list of key decisions
3. A list of action items

Return ONLY valid JSON in this exact format:

{
  "summary": "string",
  "key_decisions": ["decision 1", "decision 2"],
  "action_items": [
    {
      "task": "string",
      "owner": "string",
      "deadline": "string"
    }
  ]
}

Rules:
- Do not include markdown fences
- Do not include explanations outside JSON
- If an owner is not mentioned, use "Unassigned"
- If a deadline is not mentioned, use "Not specified"
- Keep the summary concise but informative
"""
def build_user_prompt(transcript: str, title: str | None = None) -> str:
    title_section = f"Meeting title: {title}\n\n" if title else ""

    return f"""
{title_section}Below is a meeting transcript.

Please:
- write a concise summary of the meeting
- extract the key decisions made
- extract action items with owner and deadline if mentioned

Transcript:
{transcript}
""".strip()