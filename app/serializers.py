from datetime import datetime


def serizliDict(item: dict) -> dict:
    out = item.copy()

    if isinstance(out.get('calledAt'), datetime):
        out['calledAt'] = out['calledAt'].isoformat()

    return out
