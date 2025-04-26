# Import required libraries.
from AppOpener import close, open as appopen  # Import functions to open and close apps.
from webbrowser import open as webopen  # Import web browser functionality.
from pywhatkit import search, playonyt  # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values  # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML content.
from rich import print  # Import rich for styled console output.
from groq import Groq  # Import groq for AI chat functionalities.
import webbrowser  # Import webbrowser for opening URLs.
import subprocess  # Import subprocess for interacting with the system.
import requests  # Import requests for making HTTP requests.
import keyboard  # Import keyboard for keyboard related actions.
import asyncio  # Import asyncio for asynchronous programming.
import os  # Import os for operating system functionalities.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Retrieve the Groq API key.

# Define a user agent for making HTTP requests.
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

# List to store chatbot messages.
messages = []

# System prompt for the AI chatbot.
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# Predefined common applications and their direct URLs.
COMMON_APPS = {
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://www.twitter.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "linkedin": "https://www.linkedin.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
}

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic)  # Use pywhatkit's search function to perform a Google search.
    return True  # Indicate success.

# Function to generate content using AI and save it to a file.
def Content(Topic):
    # Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'  # Default text editor.
        subprocess.Popen([default_text_editor, File])  # Open the file in Notepad.
    
    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})  # Add the user's prompt to messages.
        
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Specify the AI model.
            messages=SystemChatBot + messages,  # Include system instructions and chat history.
            max_tokens=2048,  # Limit the maximum tokens in the response.
            temperature=0.7,  # Adjust response randomness.
            top_p=1,  # Use nucleus sampling for response diversity.
            stream=True,  # Enable streaming response.
            stop=None  # Allow the model to determine stopping conditions.
        )
        
        Answer = ""  # Initialize an empty string for the response.
        
        # Process streaming response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check for content in the current chunk.
                Answer += chunk.choices[0].delta.content  # Append the content to the Answer.
        
        Answer = Answer.replace("</s>", "")  # Remove unwanted tokens from the response.
        messages.append({"role": "assistant", "content": Answer})  # Add the AI's response to messages.
        return Answer
    
    Topic = Topic.replace("Content ", "")  # Remove "Content " from the topic.
    ContentByAI = ContentWriterAI(Topic)  # Generate content using AI.
    
    # Save the generated content to a text file.
    with open(f"Data\\{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)  # Write the content to the file.
    
    OpenNotepad(f"Data\\{Topic.lower().replace(' ','')}.txt")  # Open the file in Notepad.
    return True  # Indicate success.

# Function to search a topic on YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"  # Construct the YouTube search URL.
    webbrowser.open(Url4Search)  # Open the search URL in a web browser.
    return True  # Indicate success.

# Function to play a video on YouTube.
def PlayYoutube(query):
    playonyt(query)  # Use pywhatkit's playonyt function to play the video.
    return True  # Indicate success.

# Function to open an application or relevant webpage.
def OpenApp(app):
    try:
        # Try to open the app normally.
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True  # App opened successfully.
    
    except Exception:
        print(f"App '{app}' not found. Opening in browser...")

        # Convert app name to lowercase for matching.
        app_lower = app.lower()

        # If the app is in common apps, open its official website.
        if app_lower in COMMON_APPS:
            webbrowser.open(COMMON_APPS[app_lower])
            return True

        # If not a common app, construct a direct website URL attempt.
        potential_url = f"https://www.{app_lower}.com"
        try:
            # Check if the website exists before opening.
            response = requests.get(potential_url, timeout=3)
            if response.status_code == 200:
                webbrowser.open(potential_url)
                return True
        except requests.RequestException:
            pass  # If the direct website fails, move to Google search.

        # If the app does not have a known website, do a Google search.
        search_url = f"https://www.google.com/search?q={app}+official+website"
        webbrowser.open(search_url)
        return True  # Opens Google search as a last resort.

    return False  # Indicate failure if all attempts fail.

# Function to close an application.
def CloseApp(app):
    if "chrome" in app:
        pass  # Skip if the app is Chrome.
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)  # Attempt to close the app.
            return True  # Indicate success.
        except:
            return False  # Indicate failure.

# Function to execute system-level commands.
def SystemCommand(command):
    # Access function to make the system volume.
    def mute():
        keyboard.press_and_release("volume mute")  # Simulate the mute key press.
    # Access function to update the system volume.
    def unmute():
        keyboard.press_and_release("volume mute")  # Simulate the unmute key press.
    # Access function to increase the system volume.
    def volume_up():
        keyboard.press_and_release("volume up")  # Simulate the volume up key press.
    # Access function to decrease the system volume.
    def volume_down():
        keyboard.press_and_release("volume down")  # Simulate the volume down key press.
    # Execute the dependencies command.
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True  # Indicate success.

# Function to create a new interface user command.
async def TranslateAndExecuteCommand(commands):
    funcs = []  # List to store asynchronous tasks.
    for command in commands:
        if command.startswith("open "):  # Handle "open" commands.
            app_name = command.removeprefix("open ")  # Extract the app name.
            if app_name.lower() == "1c":  # Ignore "open 1C" commands.
                pass
            elif app_name.lower() == "file":  # Ignore "open file" commands.
                pass
            else:
                fun = asyncio.to_thread(OpenApp, app_name)  # Schedule app opening.
                funcs.append(fun)
        elif command.startswith("close "):  # Handle "close" commands.
            app_name = command.removeprefix("close ")  # Extract the app name.
            fun = asyncio.to_thread(CloseApp, app_name)  # Schedule app closing.
            funcs.append(fun)
        elif command.startswith("play "):  # Handle "play" commands.
            query = command.removeprefix("play ")  # Extract the query.
            fun = asyncio.to_thread(PlayYoutube, query)  # Schedule YouTube playback.
            funcs.append(fun)
        elif command.startswith("content "):  # Handle "content" commands.
            topic = command.removeprefix("content ")  # Extract the topic.
            fun = asyncio.to_thread(Content, topic)  # Schedule content creation.
            funcs.append(fun)
        elif command.startswith("google search "):  # Handle Google search commands.
            query = command.removeprefix("google search ")  # Extract the query.
            fun = asyncio.to_thread(GoogleSearch, query)  # Schedule Google search.
            funcs.append(fun)
        elif command.startswith("youtube search "):  # Handle YouTube search commands.
            query = command.removeprefix("youtube search ")  # Extract the query.
            fun = asyncio.to_thread(YouTubeSearch, query)  # Schedule YouTube search.
            funcs.append(fun)
        elif command.startswith("system "):  # Handle system commands.
            system_command = command.removeprefix("system ")  # Extract the system command.
            fun = asyncio.to_thread(SystemCommand, system_command)  # Schedule system command.
            funcs.append(fun)
        else:
            print(f"No Function Found. For {command}")  # Print an error for unrecognized commands.

    results = await asyncio.gather(*funcs)  # Execute all tasks concurrently.

    # Process the results.
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    async for result in TranslateAndExecuteCommand(commands):  # Translate and execute commands.
        pass

    return True  # Indicate success.

# Main execution block.
if __name__ == "__main__":
    asyncio.run(Automation(['open facebook', 'open instagram', 'open telegram', 'play afsanay', 'content song for me']))