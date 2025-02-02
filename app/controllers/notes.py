from fastapi import Request
from ..utils.models import NewNote, EditNote
from typing import Optional
from ..pyscopg_connect import Connect
from psycopg2 import InterfaceError, OperationalError

async def new_note(note:NewNote, req:Request):
    note_copy = dict(note).copy()
    note_copy.update({"user_id":req.state.user_id})

    query = f"""
        INSERT INTO NOTE (title, content, tags, user_id)
        
        VALUES (%s, %s, %s, %s)
    """

    params = (
              note_copy['title'], 
              note_copy['content'], 
              note_copy['tags'], 
              note_copy['user_id']
            )

    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()

        cursor.execute(query, params)
        dbconnect.commit()

    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o
    finally:
        cursor.close()
        dbconnect.close()




async def Delete_Note(id:int, req:Request):
    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()
        cursor.execute(
            f"""
                DELETE FROM note
                WHERE note.id = %s
                AND note.user_id = %s

            """, (id, req.state.user_id,)
        )
        dbconnect.commit()
    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o
    finally:
        cursor.close()
        dbconnect.close()






async def modify_note(note:EditNote, id:int, req:Request):
    note.model_dump_json(exclude_none=True, exclude_defaults=True)

    query = f"""
                UPDATE note
                SET
                    title = COALESCE(%s, title),
                    content = COALESCE(%s, content),
                    tags = COALESCE(%s, tags),
                    is_archived = COALESCE(%s, is_archived)
                WHERE
                    note.id = %s
                AND
                    note.user_id = %s
            """

    params = (
        note.title, 
        note.content, 
        note.tags, 
        note.is_archived, 
        id, 
        req.state.user_id,
    )

    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()

        cursor.execute(query, params)
        dbconnect.commit()
    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o
    finally:
        cursor.close()
        dbconnect.close()





async def fetch_notes(req:Request, parameter:Optional[str]=None, tag:Optional[str]=None):
    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()
        query = f"""
                SELECT * 
                FROM note
                WHERE note.user_id = '{req.state.user_id}'
                AND (
                    ('{tag}' IS NULL AND '{parameter}' IS NULL)
                    OR ('{tag}'::text IS NOT NULL AND '{tag}'::text = 'all' AND note.is_archived = FALSE)
                    OR
                    ('{tag}' IS NOT NULL AND tags @> ARRAY['{tag}'])
                    OR 
                    ('{parameter}' = 'archived' AND note.is_archived = true)
                    OR
                    ('{parameter}' IS NOT NULL AND '{parameter}' != 'archived' AND (content ILIKE '%' || '{parameter}' || '%' OR title ILIKE '%' || '{parameter}' || '%'))
                )
            ORDER BY created_at DESC;
        """
        cursor.execute(query)
        notes = cursor.fetchall()
    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o
    finally:
        cursor.close()
        dbconnect.close()

    return notes