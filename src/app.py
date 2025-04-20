"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from pathlib import Path
import json

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# In-memory database for teacher credentials
teachers = {
    "teacher1": "password1",
    "teacher2": "password2"
}

# Token storage (for simplicity, not secure)
active_tokens = set()

# Load activities from JSON file
activities_file = current_dir / "activities.json"
with open(activities_file, "r") as file:
    activities = json.load(file)["activities"]


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username in teachers and teachers[form_data.username] == form_data.password:
        token = f"token-{form_data.username}"
        active_tokens.add(token)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/activities/{activity_name}/register")
def register_student(activity_name: str, email: str, token: str = Depends(oauth2_scheme)):
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already registered")

    activity["participants"].append(email)
    return {"message": f"Registered {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_student(activity_name: str, email: str, token: str = Depends(oauth2_scheme)):
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not registered")

    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
