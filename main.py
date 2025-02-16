from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,sessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title: str
    content: str
    user_id: int

class UserBase(BaseModel):
    username: str

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}

@app.post("/users/",status_code=status.HTTP_201_CREATED)
async def create_user(user:UserBase,db:db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()

@app.get("/users/",status_code=status.HTTP_200_OK)
async def read_user(user_id:int,db:db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404,detail='user not found')
    return user

@app.post("/posts/",status_code=status.HTTP_201_CREATED)
async def create_post(post:PostBase,db:db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()    

@app.get("/findPostByUser/{user_id}",status_code=status.HTTP_200_OK)
async def findPostByUser(user_id:int,db:db_dependency):
    posts  = db.query(models.Post).filter(models.Post.user_id==user_id).all()
    if posts is None:
        raise HTTPException(status_code=404,detail="no post found")
    return posts 

@app.delete("/deletePost/{post_id}",status_code=status.HTTP_200_OK)
async def deletePost(post_id:int,db:db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404,detail="no post found")
    db.delete(post)
    db.commit()

@app.put("/updatePost/{post_id}",status_code=status.HTTP_200_OK)
async def updatePost(post_id:int,postData:PostBase,db:db_dependency):
    post =db.query(models.Post).filter(models.Post.id==post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="no post found")
    post.title = postData.title
    post.content = postData.content
    db.commit()
    db.refresh(post)
    
    return {"message": "Post updated successfully", "post": post}  

class ContentUpdate(BaseModel):
    content : str

@app.patch("/updatePostContent/{post_id}",status_code=status.HTTP_200_OK)
async def updatePostcontent(post_id:int,postData:ContentUpdate,db:db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id)
    if post is None:
        raise HTTPException(status_code=404,detail="post not found")
    post.content = postData.content
    db.commit()
    db.refresh(post)
    
    return {"message": "Post content updated successfully", "post": post}  