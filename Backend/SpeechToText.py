import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import mtranslate as mt
import time

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Get the input language setting from the environment variables.
InputLanguage = env_vars.get("InputLanguage", "hi-IN")  # Default to Hindi if not set

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{lang}';  
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript + " ";
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
            }
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''.replace("{lang}", InputLanguage)

# Ensure the "Data" directory exists
data_folder = os.path.join(os.getcwd(), "Data")
os.makedirs(data_folder, exist_ok=True)

# Define the path for the HTML file.
html_file_path = os.path.join(data_folder, "Voice.html")

# Write the modified HTML code to the file.
with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Generate the file path for accessing the HTML file.
Link = f"file:///{html_file_path}"

# Set Chrome options for the WebDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--disable-gpu")  
chrome_options.add_argument("--no-sandbox")  
chrome_options.add_argument("--headless")  # Run in headless mode

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
TempDirPath = os.path.join(os.getcwd(), "Frontend", "Files")

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    os.makedirs(TempDirPath, exist_ok=True)  # Ensure directory exists
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    if not Query:  
        return ""
    query_words = Query.lower().strip().split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", 
                      "what's", "where's", "how's", "can you"]

    # Check if the query is a question and add a question mark if necessary.
    if any(word + " " in Query.lower() for word in question_words):
        Query = Query.rstrip('.!?') + "?"
    else:
        Query = Query.rstrip('.!?') + "."

    return Query.capitalize()

# Function to translate text into English using the mtranslate library.
def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize() if Text else ""

# Function to perform speech recognition using the WebDriver.
def SpeechRecognition():
    try:
        # Open the HTML file in the browser.
        driver.get(Link)
        print("HTML file loaded.")

        # Wait for the start button to be clickable and click it.
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "start"))).click()
        print("Speech recognition started.")

        # Wait for the output element to contain text.
        WebDriverWait(driver, 30).until(lambda d: d.find_element(By.ID, "output").text.strip() != "")
        Text = driver.find_element(By.ID, "output").text
        print(f"Recognized text: {Text}")

        # Stop recognition by clicking the stop button.
        driver.find_element(By.ID, "end").click()
        print("Speech recognition stopped.")

        return Text.strip()
    except Exception as e:
        print(f"Error during speech recognition: {e}")
        return None

# Main execution block.
if __name__ == "__main__":
    try:
        while True:
            Text = SpeechRecognition()
            if Text:  
                if "en" in InputLanguage.lower():
                    print("Modified Query:", QueryModifier(Text))
                else:
                    SetAssistantStatus("Translating...")
                    print("Translated Query:", QueryModifier(UniversalTranslator(Text)))
            time.sleep(2)  
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()  # Close the browser when done.