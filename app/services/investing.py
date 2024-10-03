from datetime import datetime

from app.models.base import AbstractModelForInvest


def investing(
    target: AbstractModelForInvest,
    sources: list[AbstractModelForInvest],
) -> list[AbstractModelForInvest]:
    updated = []
    for source in sources:
        invest = min(
            source.full_amount - source.invested_amount,
            target.full_amount - target.invested_amount,
        )
        for obj in (target, source):
            obj.invested_amount += invest
            if obj.invested_amount == obj.full_amount:
                obj.fully_invested = True
                obj.close_date = datetime.now()
        updated.append(obj)

        if target.fully_invested:
            break
    return updated
