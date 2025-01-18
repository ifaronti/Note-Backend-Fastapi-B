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
                FROM notes
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
    try:
        await prisma.connect()
        await prisma.query_raw(
            f"""
                UPDATE note
                SET
                    title = COALESCE('{note.title}', note.title)
                    content = COALESCE('{note.content}', note.content)
                    tags = COALESCE('{note.tags}', note.tags)
                    is_archived = COALESCE('{note.isArchived}', note.is_archived)
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

    