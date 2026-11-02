import uvicorn

if __name__ == "__main__":
    uvicorn.run("runtime.motion.service:app", host="127.0.0.1", port=16525, workers=1, access_log=False)
