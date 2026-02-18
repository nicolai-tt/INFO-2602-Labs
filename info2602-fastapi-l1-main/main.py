from fastapi import FastAPI
import json

app = FastAPI()

# Load data
with open('./data.json') as f:
    data = json.load(f)

@app.get('/')
async def hello_world():
    return "Hello, World!"


@app.get('/students')
async def get_students(pref: str | None = None):
    if pref:
        return [student for student in data if student['pref'] == pref]
    return data

@app.get('/stats')
async def get_stats():
    stats = {}

    for student in data:
        
        meal = student['pref']
        if meal in stats:
            stats[meal] += 1
        else:
            stats[meal] = 1

        programme = student['programme']
        if programme in stats:
            stats[programme] += 1
        else:
            stats[programme] = 1

    return stats

# Example tests 

# http://127.0.0.1:8000/add/8/4

# http://127.0.0.1:8000/subtract/8/4

# http://127.0.0.1:8000/multiply/8/4 

# http://127.0.0.1:8000/divide/8/4

@app.get("/add/{a}/{b}")
def add(a, b):
    return int(a) + int(b)


@app.get("/subtract/{a}/{b}")
def subtract(a, b):
    return int(a) - int(b)


@app.get("/multiply/{a}/{b}")
def multiply(a, b):
    return int(a) * int(b)


@app.get("/divide/{a}/{b}")
def divide(a, b):
    if int(b) == 0:
        return "Cannot divide by zero"
    return int(a) / int(b)


