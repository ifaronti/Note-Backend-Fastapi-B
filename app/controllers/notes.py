from prisma import Prisma
from fastapi import Request
from ..utils.models import NewNote, EditNote
from typing import Optional

prisma = Prisma()


async def fetch_tags(req:Request):
    try:
        await prisma.connect()
        tags = await prisma.query_raw(
            f"""
                SELECT tags
                FROM note
                WHERE note.user_id = '{req.state.user_id}'
            """
        )
    except:
        raise
    finally:
        await prisma.disconnect()

    return tags






async def new_note(note:NewNote, req:Request):
    note_copy = dict(note).copy()
    note_copy.update({"user_id":req.state.user_id})
    try:
        await prisma.connect()
        await prisma.note.create(data=note_copy)
    except:
        raise
    finally:
        await prisma.disconnect()






async def Delete_Note(id:int, req:Request):
    try:
        await prisma.connect()
        await prisma.query_raw(
            f"""
                DELETE FROM note
                WHERE note.id = {id}
                AND note.user_id = '{req.state.user_id}'
            """
        )
    except:
        raise
    finally:
        await prisma.disconnect()






async def modify_note(note:EditNote, id:int, req:Request):
    note.model_dump_json(exclude_none=True)
    note_copy = dict(note).copy()

    for i in note_copy:
        if i == False:
            del note_copy[i]

    try:
        await prisma.connect()
        await prisma.query_raw(
            f"""
                UPDATE note
                SET
                    title = COALESCE('{note_copy["title"]}', title),
                    content = COALESCE('{note_copy["content"]}', content),
                    tags = COALESCE('{{{note_copy["tags"]}}}', tags),
                    is_archived = COALESCE('{note_copy["isArchived"]}', is_archived)
                WHERE
                    note.id = '{id}'
                AND
                    note.user_id = '{req.state.user_id}'
            """
        )
    except:
        raise
    finally:
        await prisma.disconnect()





async def fetch_notes(req:Request, parameter:Optional[str]=None):
    try:
        await prisma.connect()
        where_conditions = {
        "user_id": req.state.user_id,
        }

    
        if parameter:
            where_conditions['OR'] = [
                {'content': {'contains': parameter, 'mode': 'insensitive'}},
                {'tags': {'has': parameter}}, 
                {'title': {'contains': parameter, 'mode': 'insensitive'}}
            ]
        

        notes = await prisma.note.find_many(where=where_conditions)
    except:
        raise
    finally:
        await prisma.disconnect()

    return notes

    