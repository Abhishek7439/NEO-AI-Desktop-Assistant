from googlesearch import search
from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump  # Importing functions to read and write JSON files.
import datetime  # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv_values to read environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client with the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define the system instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try to load the chat log from a JSON file, or create an empty one if it doesn't exist.
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)


# Function to perform a Google search and return only the most relevant answer.
def GoogleSearch(query):
    results = search(query, advanced=True, num_results=3)  # Fetch top 3 results for speed
    Answer = ""

    for result in results:
        if result.description:
            Answer = result.description  # Get the most relevant answer
            break  # Stop after the first relevant result

    return Answer if Answer else "No relevant answer found."


# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    return "\n".join(line for line in Answer.split('\n') if line.strip())

# Predefined chatbot conversation system message.
SystemChatBot = [{"role": "system", "content": System}]

# Function to get real-time information like the current date and time.
def Information():
    now = datetime.datetime.now()
    return f"Use This Real-time Information if needed:\nDate & Time: {now.strftime('%A, %d %B %Y, %H:%M:%S')}"

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load the chat log from the JSON file.
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    
    messages.append({"role": "user", "content": prompt})

    # Get Google search results asynchronously.
    google_results = GoogleSearch(prompt)

    # Add search results and real-time information to chatbot memory.
    SystemChatBot.append({"role": "system", "content": google_results})
    SystemChatBot.append({"role": "system", "content": Information()})

    # Generate a response using the Groq client.
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    # Process response.
    Answer = "".join(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
    Answer = Answer.strip().replace("</s>", "")

    messages.append({"role": "assistant", "content": Answer})

    # Save chat log.
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    # Remove the last system message to keep context fresh.
    SystemChatBot.pop()

    return AnswerModifier(Answer)

# Main entry point of the program for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
