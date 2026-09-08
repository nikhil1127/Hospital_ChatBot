from fastapi import FastAPI
from app.api.webhook import router as webhook_router

app = FastAPI(title="Multispeciality Hospital Bot")

# Include the webhook routes
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Hospital Bot Server is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
