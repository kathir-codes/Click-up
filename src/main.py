import logging

from fastapi import FastAPI
from src.exceptions.graphql_error_handler import CustomGraphQLRouter
from src.logging.config import setup_logging
from fastapi.middleware.cors import CORSMiddleware
from src.modules.graphql_schema import schema
from src.middleware.request_id import request_id_middleware
from src.middleware.request_logging import request_logging_middleware
# Configure logging first
setup_logging()

logger = logging.getLogger(__name__) #current module name

# Create FastAPI application
app = FastAPI(title="ClickUp Backend")
app.middleware("http")(request_logging_middleware)
app.middleware("http")(request_id_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register Strawberry GraphQL
graphql_app = CustomGraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

logger.info("ClickUp backend application initialized")


@app.get("/")
def root():
    return {"message": "ClickUp Backend is running"}

