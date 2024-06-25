import uvicorn
from fastapi import FastAPI
import app.api.endpoints.routes as routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS to allow any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api/v1")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
