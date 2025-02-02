from fastapi import Request
from ..pyscopg_connect import Connect
from psycopg2  import InterfaceError, OperationalError



async def fetch_tags(req:Request):
    try:
        dbconnect = Connect().dbconnect()
        cursor = dbconnect.cursor()
        cursor.execute(
            f"""
            SELECT json_agg(DISTINCT tag) AS tags
            FROM (
                SELECT unnest(note.tags) AS tag
                FROM note
                WHERE note.user_id = %s
            ) AS flattened_tags
            """, (req.state.user_id,)
        )
        tags = cursor.fetchone()

    except InterfaceError as i:
        raise i
    except OperationalError as o:
        raise o
    finally:
        cursor.close()
        dbconnect.close()

        dict(tags)["tags"]
    return dict(tags)["tags"]