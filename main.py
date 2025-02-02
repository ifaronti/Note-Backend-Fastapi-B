from fastapi import FastAPI
from app.routers import user, notes
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

app = FastAPI()

app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization", "X-Custom-Header"] 
)

app.include_router(user.router)
app.include_router(notes.router)

@app.get('/')
def Welcome():
    return 'Listen To: Rakim - Holy Are You'

handler = Mangum(app)

# find . -type d -name __pycache__ -exec rm -r {} \+
