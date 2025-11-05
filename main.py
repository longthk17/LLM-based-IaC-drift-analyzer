import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "api:app",  # tên file : object FastAPI
        host="0.0.0.0",
        port=8000,
        reload=True,  # bật reload để dev code auto refresh
    )
