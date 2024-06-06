import sys

import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from TodoApplicationWithRoutes.company import company_apies, dependencies
from fastapi import FastAPI, Depends
from TodoApplicationWithRoutes import models
from TodoApplicationWithRoutes.database import engine
from TodoApplicationWithRoutes.routes import auth, todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router, )
app.include_router(todos.router, )
app.include_router(
    company_apies.router,
    prefix="/company",
    tags=["company"],
    dependencies=[Depends(dependencies.get_token_header)],
    responses={4018: {'description': 'external use only'}}
)
