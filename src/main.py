from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.modules.graphql_schema import schema

app = FastAPI(title="ClickUp Backend")

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    return {"message": "ClickUp Backend is running"}