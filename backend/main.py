from fastapi import FastAPI
from backend.routes import user_routes
from backend.routes import income_routes
from backend.routes import expense_routes
from backend.routes import investment_routes
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(user_routes.router)
app.include_router(income_routes.router)
app.include_router(expense_routes.router)
app.include_router(investment_routes.router)

@app.get("/")
def health_check():
    return {"message": "API is running!"}