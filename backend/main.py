import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Python Code Review App!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)