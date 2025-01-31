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
                WHERE note.id = $1
                AND note.user_id = $2

            """, id, req.state.user_id
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
                    note.user_id = $6
            """
        , note.title, note.content, note.tags, note.is_archived, id, req.state.user_id)
    except:
        raise
    finally:
        await prisma.disconnect()





async def fetch_notes(req:Request, parameter:Optional[str]=None, tag:Optional[str]=None):
    try:
        await prisma.connect()
        query = """
                SELECT * 
                FROM note
                WHERE note.user_id = $1
                AND (
                    ($2::text IS NULL AND $3::text IS NULL)
                    OR ($2::text IS NOT NULL AND $2::text = 'all' AND note.is_archived = FALSE)
                    OR
                    ($2 IS NOT NULL AND tags @> ARRAY[$2])
                    OR 
                    ($3 = 'archived' AND note.is_archived = true)
                    OR
                    ($3 IS NOT NULL AND $3 != 'archived' AND (content ILIKE '%' || $3 || '%' OR title ILIKE '%' || $3 || '%'))
                )
            ORDER BY created_at DESC;
        """
        notes = await prisma.query_raw(
            query, 
            req.state.user_id,  # $1
            tag,                # $2
            parameter           # $3
        )
    except:
        raise
    finally:
        await prisma.disconnect()

    return notes