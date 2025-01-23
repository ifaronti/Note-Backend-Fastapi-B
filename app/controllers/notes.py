from prisma import Prisma
from fastapi import Request
from ..utils.models import NewNote, EditNote
from typing import Optional

prisma = Prisma()

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

    try:
        await prisma.connect()
        await prisma.query_raw(
            f"""
                UPDATE note
                SET
                    title = COALESCE($1, title),
                    content = COALESCE($2, content),
                    tags = COALESCE($3, tags),
                    is_archived = COALESCE($4, is_archived)
                WHERE
                    note.id = $5
                AND
                    note.user_id = '{req.state.user_id}'
            """
        , note.title, note.content, note.tags, note.is_archived, id)
    except:
        raise
    finally:
        await prisma.disconnect()





async def fetch_notes(req:Request, parameter:Optional[str]=None):
    try:
        await prisma.connect()
 
        notes = await prisma.query_raw(f"""
            SELECT * 
            FROM note
            WHERE user_id = '{req.state.user_id}' 
            OR (user_id = '{req.state.user_id}' AND
                ('{parameter}' = 'archived' AND is_archived = TRUE) 
                OR (
                ('{parameter}' IS NOT NULL AND 
                (content ILIKE '%{parameter}%' 
                OR tags @> ARRAY['{parameter}'] 
                OR title ILIKE '%{parameter}%')
                )
                )
            )
            ORDER BY created_at DESC;
        """)
    except:
        raise
    finally:
        await prisma.disconnect()

    return notes

    