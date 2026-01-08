import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the prompt template
def load_prompt_template():
    try:
        with open("prompt_template.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        # Default template in case file doesn't exist
        return """Please provide information about insurance and extract key criteria in JSON format."""

# Function to get AI response
def get_ai_response(prompt, system_prompt=None):
    """
    Get a response from the OpenAI model
    
    Args:
        prompt (str): The user's message
        system_prompt (str): Optional custom system prompt
        
    Returns:
        str: The AI's response
    """
    # Force reload environment variables
    load_dotenv(override=True)
    token = os.environ.get("GITHUB_TOKEN")
    endpoint = "https://models.inference.ai.azure.com"
    model_name = "gpt-4o-mini"
    
    print(f"Token: {token[:10]}... (truncated)")  # Print only first 10 chars for security
    print(f"Endpoint: {endpoint}")
    print(f"Model: {model_name}")
    
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not found. Please check your .env file.")
    
    try:
        client = OpenAI(
            base_url=endpoint,
            api_key=token,
        )
        
        # Get the prompt template
        template = load_prompt_template()
        print("Loaded template:", template[:100] + "..." if len(template) > 100 else template)
        
        # Construct the full prompt using the template
        full_prompt = f"{template}\n\nUser Query: {prompt}"
        
        # Use a default system prompt if none provided
        if system_prompt is None:
            system_prompt = "You are InsureBot, an AI assistant specializing in insurance. Provide helpful information about insurance in a structured format."
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model=model_name,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        # Return a fallback message if there's an error
        print(f"Error getting AI response: {e}")
        return "I'm sorry, I couldn't process that request. Could you please try again?"

# Example usage (will only run if script is executed directly)
if __name__ == "__main__":
    test_prompt = "What is a deductible in health insurance? Also, can you find me plans for a 35-year-old non-smoker with a budget of $300/month?"
    print(get_ai_response(test_prompt))