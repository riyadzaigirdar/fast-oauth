import bcrypt
import jwt
from fastapi import FastAPI, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

app = FastAPI()

JWT_SECRET = "mysecret"


oauth2_sceme = OAuth2PasswordBearer(tokenUrl='token')


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.TextField()

    def verify_password(self, password):
        verify = bcrypt.checkpw(password.encode("utf-8"), eval(self.password))
        return verify


User_model = pydantic_model_creator(
    User, name="User_Model", exclude=["password"])
User_form = pydantic_model_creator(
    User, name="User_Form", exclude_readonly=True)


@app.post("/create", response_model=User_model)
async def create(user: User_form):
    obj = User(username=user.username, password=bcrypt.hashpw(
        user.password.encode("utf-8"), bcrypt.gensalt()))
    await obj.save()
    return await User_model.from_tortoise_orm(obj)


# @app.post("/token", status_code=200)
# async def login(data: User_form, response: Response):
#     obj = await User.get(username=data.username)
#     if obj:
#         verified = obj.verify_password(data.password)
#         if verified:
#             return {"status": "success", "msg": "jwt token"}
#         else:
#             response.status_code = 401
#             return {"status": "failed", "msg": "Password doesn't match"}
#     else:
#         response.status_code = 400
#         return {"status": "failed", "msg": "Account with that email doesn't exist"}


@app.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    obj = await User.get(username=form_data.username)
    if obj:
        verified = obj.verify_password(form_data.password)
        if verified:
            token = jwt.encode(
                {"username": obj.username, "id": obj.id}, JWT_SECRET)
            return {"status": "success", "msg": "jwt token", "data": token}
        else:
            response.status_code = 401
            return {"status": "failed", "msg": "Password doesn't match"}
    else:
        response.status_code = 400
        return {"status": "failed", "msg": "Account with that email doesn't exist"}

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["main"]},
    generate_schemas=True,
    add_exception_handlers=True
)
