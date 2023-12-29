from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from chat.api.routers.api_v1 import api_router

app = FastAPI(title="TG BOT API", version="0.0.1")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
