import cohere  # Import the Cohere library for AI services.
from rich import print  # Import the Rich library to enhance terminal outputs.
from dotenv import dotenv_values  # Import dotenv to load environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve API key.
CohereAPIKey = env_vars.get("CohereAPIKey")

# Check if API key is loaded properly
if not CohereAPIKey:
    raise ValueError("Cohere API key not found! Please check your .env file.")

# Create a Cohere client using the provided API key.
co = cohere.Client(api_key=CohereAPIKey)

# Define a list of recognized function keywords for task categorization.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# Define the preamble that guides the AI model on how to categorize queries.
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write an application and open it in notepad'.
*** Do not answer any query, just decide what kind of query is given to you. ***

-> Respond with 'general ( query )' if the query can be answered by a chatbot without requiring real-time information.
-> Respond with 'realtime ( query )' if the query requires up-to-date information like recent news, live sports scores, etc.
-> Respond with 'open (application name)' if the query asks to open an application.
-> Respond with 'close (application name)' if the query asks to close an application.
-> Respond with 'play (song name)' if the query asks to play a song.
-> Respond with 'generate image (image prompt)' if the query requests an AI-generated image.
-> Respond with 'reminder (datetime with message)' if the query asks to set a reminder.
-> Respond with 'system (task name)' for system-related tasks like mute, unmute, volume up, etc.
-> Respond with 'content (topic)' for requests to generate content.
-> Respond with 'google search (topic)' for Google searches.
-> Respond with 'youtube search (topic)' for YouTube searches.
-> Respond with 'exit' if the user wants to end the conversation.

*** If multiple tasks are mentioned, respond with separate commands like 'open facebook, open telegram, close whatsapp'. ***
*** If unsure, classify it as 'general (query)'. ***
"""

# Define a chat history with predefined user-chatbot interactions for context.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and remind me that i have a dance performance on 5th Aug"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 5th Aug dance performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]

# Function to classify queries using Cohere API
def FirstLayerDMM(prompt: str):
    """
    This function sends the user's query to the Cohere AI model
    and classifies it based on predefined categories.
    """
    try:
        # Create a streaming chat session with the Cohere model.
        stream = co.chat_stream(
            model='command-r-plus',  # Specify the Cohere model to use.
            message=prompt,  # Pass the user's query.
            temperature=0.7,  # Set the creativity level of the model.
            chat_history=ChatHistory,  # Provide predefined chat history for context.
            prompt_truncation='OFF',  # Ensure the prompt is not truncated.
            connectors=[],  # No additional connectors are used.
            preamble=preamble  # Pass the detailed instruction preamble.
        )

        # Initialize an empty string to store the generated response.
        response = ""

        # Iterate over events in the stream and capture text generation events.
        for event in stream:
            if event.event_type == "text-generation":
                response += event.text  # Append generated text to the response.

        # Clean and process the response
        response = response.replace("\n", "").strip()
        response_parts = [part.strip() for part in response.split(",")]

        return response_parts

    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        return ["general error occurred"]

# Test the function with sample queries
if __name__ == "__main__":
    while True:
        user_input = input(">>>")
        if user_input.lower() in ["exit", "quit"]:
            print("[bold green]Exiting...[/bold green]")
            break
        
        results = FirstLayerDMM(user_input)
        print(f"{results}")
