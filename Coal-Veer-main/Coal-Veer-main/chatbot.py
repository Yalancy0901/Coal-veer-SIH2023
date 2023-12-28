from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from nltk.chat.util import Chat, reflections
import pymongo
from spellchecker import SpellChecker
from datetime import datetime

app = FastAPI()
myclient = pymongo.MongoClient("mongodb+srv://Minebot:chatbotmines123@chatbot.yes8jb1.mongodb.net/")
mydb = myclient["chatbots"]
users = mydb["users"]
mycol = mydb["documents"]
history = mydb["user1"]
user=None

class UserData1(BaseModel):
    username: str
    email: str
    password: str
class UserData2(BaseModel):
    username: str
    password: str
class message(BaseModel):
    message: str

def sendmongo(data):
    finding=users.find_one({"username":data["username"]})
    print(finding)
    if finding!=None:
        return 0
    else:
        users.insert_one(data)
        return 1

def receivemongo(uname, pas):
    data=users.find_one({"username":uname})
    if data is None:
        return 0
    else:
        data=users.find_one({"$and": [{"username": uname}, {"password": pas}]})
        if data is None:
            return -1
        else:
            return 1

data=[]
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/signup/")
async def signup(user_data: UserData1):
    global user
    print(user_data.dict())
    res=sendmongo(user_data.dict())
    print(res)

    if res==1:
        user = user_data.username
        return {"message": "User registered successfully"}
    else:
        return {"Message":"User is already Registered.Try to Log in"}

@app.post("/login/")
async def login(user_data: UserData2):
    global user  # Declare user as a global variable

    bol = receivemongo(user_data.username, user_data.password)
    if bol == 1:
        user = user_data.username  # Assign the value to the global variable
        return {"message": "Login Successful"}
    elif bol == -1:
        return {"message": "Invalid username or password"}
    else:
        return {"message": "User Not registered"}




'''cursor=history.find({"user":user}).sort("timestamp",1)
for i in cursor:
    print(i+"hel")
for document in cursor:
    # Extract relevant fields from the document  # Assuming "_id" is one of the fields
    field1 = document["user_input"]
    field2 = document["bot_output"]
    # Add the extracted data to the dictionary using the document_id as the key
    data.append( {
        "user_input": field1,
        "bot_output": field2,
        # Add more fields as needed
    })'''

def clear():
    history.delete_many({"user":user})

print(DeprecationWarning)

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
    history.insert_one({"user":user,"user_input":user_input,"bot_output":res,"timestamp":datetime.now()})
    return res
    #return chatbot.respond(user_input)



'''@app.get("/", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})'''

@app.get("/contact", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

app.mount("/chatbot/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/chatbot/", response_class=HTMLResponse)
async def chat_get(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/chat/")
async def chat(user_input: str = Form(...)):
    response = get_response(user_input)
    return {"response": response}

'''@app.post("/signup/")
async def signup(user_data: UserData1):
    print(user_data.dict())
    sendmongo(user_data.dict())
    return {"message": "User registered successfully"}

@app.post("/login/")
async def login(user_data: UserData2):
    print(user_data.dict())
    bol = receivemongo(user_data.username, user_data.password)
    if bol == 1:
        return {"message":"Login Successful"}
    elif bol==-1:
        return {"message": "Invalid username or password"}
    else:
        return {"message":"User Not registered"}'''
@app.get("/complaint", response_class="HTMLResponse")
async def signup_form(request: Request):
    return templates.TemplateResponse("complaint.html", {"request": request})

app.mount("/history/static", StaticFiles(directory="static"), name="static")

@app.get("/history", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

# Create a route to handle chatbot communication
@app.post("/hist/")
async def chat(messag: message):
    global user  # Ensure user is declared as a global variable
    print(user)
    cursor=history.find({"user":user}).sort("timestamp",1)
    for document in cursor:
    # Extract relevant fields from the document  # Assuming "_id" is one of the fields
        field1 = document["user_input"]
        field2 = document["bot_output"]
    # Add the extracted data to the dictionary using the document_id as the key
        data.append( {
            "user_input": field1,
            "bot_output": field2,
        # Add more fields as needed
        })
    msg = messag.dict()
    if msg["message"] == "Clear":
        print("Clear")
        history.delete_many({"user": user})
    return JSONResponse(content=data)