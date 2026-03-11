import os
from google.genai import Client
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv

# Load API key from ~/.env
home = os.path.expanduser("~")
env_path = os.path.join(home, ".env")
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# EVOLVE-BLOCK-START
PROMPT_TEMPLATE = """Task: Extract entities from the text.
Output Format: ONLY raw JSON. No conversational filler. No markdown code blocks. No backticks.
Schema: {{"Name": string, "Date": "YYYY-MM-DD", "Severity Level": "Low"|"Medium"|"High"|"Critical", "Cost": float}}

Text: {text}

JSON:"""
# EVOLVE-BLOCK-END

def extract_data(text: str) -> str:
    """
    Calls the Gemma 3 7B model via google-genai SDK to extract data based on the prompt.
    """
    client = Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
    
    prompt = PROMPT_TEMPLATE.format(text=text)
    
    response = client.models.generate_content(
        model="models/gemma-3-4b-it",
        contents=prompt,
        config=GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=400,
        )
    )
    
    return response.text.strip()

if __name__ == "__main__":
    # Test on a single example
    test_text = "Urgent email from Alice Smith dated 2022-03-04. I'm not sure if this is relevant, but The server crash is Low level. Loss estimated at $259.83."
    try:
        print(extract_data(test_text))
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
