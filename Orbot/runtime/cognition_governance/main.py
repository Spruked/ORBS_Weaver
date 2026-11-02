import uvicorn

if __name__ == "__main__":
    uvicorn.run("runtime.cognition_governance.service:app", host="127.0.0.1", port=16524, workers=1)
