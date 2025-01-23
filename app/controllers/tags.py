from prisma import Prisma
from fastapi import Request

prisma = Prisma()


async def fetch_tags(req:Request):
    try:
        await prisma.connect()
        tags = await prisma.query_raw(
            f"""
            SELECT json_agg(DISTINCT tag) AS tags
            FROM (
                SELECT unnest(note.tags) AS tag
                FROM note
                WHERE note.user_id = $1
            ) AS flattened_tags
            """, req.state.user_id
        )

    except:
        raise
    finally:
        await prisma.disconnect()

    return tags[0]["tags"]

