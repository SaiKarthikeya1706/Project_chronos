● Project Title: Project Chronos: The AI Archeologist.
● Student Name(s) and ID(s) - Naga Sai Karthikeya Maram and SE25UCSE084
● Project Description: Project Chronos is an AI-powered application designed to digitally reconstruct and contextualize fragmented pieces of old internet content — such as forum posts, chat logs, or web archives. Using Google Gemini, it intelligently fills in missing text, interprets outdated slang, and restores linguistic coherence. The system then leverages Google Custom Search to automatically discover relevant articles, definitions, and cultural references that explain the reconstructed content. Finally, it compiles a structured Reconstruction Report containing the original fragment, the AI’s reconstructed version, and contextual sources — helping researchers, historians, and enthusiasts rediscover and understand the cultural fabric of the early digital age.
● Setup Instructions: 
 - Install python 3.11.4
 - Once installation completed. Go to the path where 'requirements.txt' present in the folder structure.
 - Run command 'pip install -r requirements.txt'
 - Once required python packages installed.
 - Fill the environment variables in '.env' file with variables: GEMINI_API_KEY, GOOGLE_SEARCH_API_KEY, GOOGLE_CSE_ID
 - Run command 'python chronos.py' to run the application.
 - Enter user input and the python program will generate the report.