from fastapi import APIRouter, Depends, status, Request
from ..dependencies.token import verify_token
from pydantic import BaseModel as model
from typing import Optional
from ..utils.models import GetResponse, GenericResponse, EditNote, NewNote, GetNotes
from ..controllers.notes import fetch_notes, Delete_Note, modify_note, new_note
from ..controllers.tags import fetch_tags

router = APIRouter(
    prefix="/api/notes",
    dependencies=[Depends(verify_token)],
    # responses=status.HTTP_200_OK,
    tags=["All Notes Routes"]
)


class GetTags(model):
    tags: Optional[list]=[]
    success:bool
    message:str


@router.get("/tags", response_model=GetTags)
async def Tags(req:Request):
    tags = await fetch_tags(req=req)
    return {"tags":tags, "success":True, "message":"All tags in notes"}


@router.get("", response_model=GetNotes)
async def Get_Notes(req:Request, parameter:Optional[str]=None):
    notes = await fetch_notes(req, parameter)
    return {"success":True, "data":notes}




@router.delete("/{id}", response_model=GenericResponse)
async def Delete(id:int, req:Request):
    await Delete_Note(id, req)
    return {"success":True, "message":'Note deleted permanently'}



@router.patch("/note/{id}", response_model=GenericResponse)
async def Edit_Note(note:EditNote, req:Request, id:int):
    await modify_note(note, req=req, id=id)
    return {"success":True, "message":"Note updated successfully"}




@router.post("/new", response_model=GenericResponse)
async def Create_Note(note:NewNote, req:Request):
    await new_note(note=note, req=req)
    return {"success":True, "message":'new note added to your collection'}