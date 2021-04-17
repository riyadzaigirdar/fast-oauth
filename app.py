from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

oauth2_sceme = OAuth2PasswordBearer(tokenUrl='token')


@app.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return {"token": form_data.username + "token"}


@app.get("/")
async def index(token: str = Depends(oauth2_sceme)):
    return {"the_token": token}
