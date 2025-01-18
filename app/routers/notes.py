from fastapi import APIRouter, Depends, status, Request
from ..dependencies.token import verify_token
from pydantic import BaseModel as model
from typing import Optional
from ..utils.models import GetResponse, GenericResponse, EditNote, NewNote
from ..controllers.notes import fetch_tags, fetch_notes, Delete_Note, modify_note, new_note

router = APIRouter(
    prefix="/api/notes",
    dependencies=[Depends(verify_token)],
    # responses=status.HTTP_200_OK,
    tags=["All Notes Routes"]
)


class GetTags(model):
    tags: list
    success:bool
    messsage:str


@router.get("/tags", response_model=GetTags)
async def Tags(req:Request):
    tags = await fetch_tags(req=req)
    return {"tags":tags, "success":True, "message":"All tags in notes"}




@router.get("", response_model=GetResponse)
async def Get_Notes(req:Request, parameter:Optional[str]=None):
    notes = await fetch_notes(req, parameter)
    return {"success":True, "data":notes}



@router.delete("/{id}", response_model=GenericResponse)
async def Delete(id:int):
    await Delete_Note(id)
    return {"success":True, "message":'Note deleted permanently'}



@router.patch("/note", response_model=GenericResponse)
async def Edit_Note(note:EditNote, req:Request):
    await modify_note(note, req=req)



@router.post("/new", response_model=GenericResponse)
async def Create_Note(note:NewNote, req:Request):
    await new_note(note=note, req=req)
    return {"success":True, "message":'new note added to your collection'}