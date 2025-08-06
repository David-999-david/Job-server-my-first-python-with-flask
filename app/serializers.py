from datetime import datetime


def serizliDict(item: dict) -> dict:
    out = item.copy()

    if isinstance(out.get('calledAt'), datetime):
        out['calledAt'] = out['calledAt'].isoformat()

    if isinstance(out.get('created_at'), datetime):
        out['created_at'] = out['created_at'].isoformat()

    if isinstance(out.get('updated_at'), datetime):
        out['updated_at'] = out['updated_at'].isoformat()

    return out
