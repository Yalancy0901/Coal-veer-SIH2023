from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from nltk.chat.util import Chat, reflections
import pymongo
from spellchecker import SpellChecker
from datetime import datetime

myclient = pymongo.MongoClient("mongodb+srv://Minebot:chatbotmines123@chatbot.yes8jb1.mongodb.net/")
mydb = myclient["chatbots"]
mycol = mydb["documents"]
history = mydb["user1"]

# Create a FastAPI application
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")  # Serve static files from the "static" directory
templates = Jinja2Templates(directory="templates")

# Define pairs of patterns and responses using regular strings
pairs = [
    [
        "hello|hi|hey",
        ["Hello!", "Hi there!", "How can I assist you today?"],
    ],
    [
        "what is your name|who are you",
        ["You can call me Coal BOT."],
    ],
    [
        "how are you",
        ["I'm just a computer program, so I don't have feelings, but I'm here to assist you!"],
    ],
    [
        "what can you do|help",
        ["I can provide information, answer questions, about Coal Mines Act. Just ask!"],
    ],
    [
        "bye|goodbye",
        ["Goodbye!", "Have a great day!"],
    ],
    [
        "(.*)",
        [
            "I'm sorry, I don't understand that.",
            "I'm not sure I follow. Can you rephrase your question?",
            "I didn't quite catch that. Please ask again.",
        ],
    ],
]
x = mycol.find()
j=3
for i in x:
    a=[i["input"],[i["responses"]],]
    pairs.insert(j,a)
    j+=1

# Create a chatbot instance
chatbot = Chat(pairs, reflections)

spell_checker = SpellChecker()

def spell_check(user_input):
    # Perform spelling correction
    corrected_input = []
    for word in user_input.split():
        corrected_word = spell_checker.correction(word)
        corrected_input.append(corrected_word)
    corrected_input = " ".join(corrected_input)
    
    # Get a response from the chatbot
    return corrected_input
# Function to get a response from the chatbot
def get_response(user_input):
    #user_input=spell_check(user_input)
    corrected_input = spell_check(user_input)
    res=chatbot.respond(corrected_input)
    history.insert_one({"user_input":user_input,"bot_output":res,"timestamp":datetime.now()})
    return res
    #return chatbot.respond(user_input)

# Create a route to render the chat interface
@app.get("/chatbot", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Create a route to handle chatbot communication
@app.post("/chat/")
async def chat(user_input: str = Form(...)):
    response = get_response(user_input)
    return {"response": response}