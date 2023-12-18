import datetime
from typing import Any, Generator

from loguru import logger
from pymongo import MongoClient

from app.config import settings
from app.models import Transaction

DATABASE = settings.DATABASE
USER_SMART_TRANSACTIONS_COLLECTION = settings.USER_SMART_TRANSACTIONS_COLLECTION
USER_SMART_TRANS_SCORE_COLLECTION = settings.USER_SMART_TRANS_SCORE_COLLECTION
TRANSACTIONS_COLLECTION = settings.TRANSACTIONS_COLLECTION


def get_last_update_datetime(client: MongoClient[dict[str, Any]]) -> datetime.datetime:
    collection = client[DATABASE][USER_SMART_TRANSACTIONS_COLLECTION]

    result = collection.find_one(
        projection={"_id": 0, "HistoryLastUpdated": 1},
        sort=[("HistoryLastUpdated", -1)],
        limit=1,
    )

    if result is None:
        return datetime.datetime.utcnow() - datetime.timedelta(days=1)

    return result["HistoryLastUpdated"]


def set_probability_score(
    transaction: Transaction, client: MongoClient[dict[str, Any]]
) -> None:
    collection = client[DATABASE][USER_SMART_TRANSACTIONS_COLLECTION]

    pipeline = [
        {
            "$match": {
                "UserId": transaction.UserId,
                "CompanyId": transaction.ProjectCompanyId,
            }
        },
        {"$unwind": "$History"},
        {
            "$match": {
                "History.Project.Id": transaction.ProjId,
                "History.Resource.Id": transaction.MachineId,
                "History.Task.Id": transaction.ActivityId,
            }
        },
        {
            "$project": {
                "_id": 0,
                "TransId": transaction.TransactionId,
                "Score": {"$divide": ["$History.TransactionCount", "$TotalCount"]},
            }
        },
        {"$merge": {"into": USER_SMART_TRANS_SCORE_COLLECTION}},
    ]

    collection.aggregate(pipeline)

    logger.info(f"Set probability score for transaction {transaction.TransactionId}")


def get_recent_transaction(
    datetime_from: datetime.datetime, client: MongoClient[dict[str, Any]]
) -> Generator[Transaction, None, None]:
    collection = client[DATABASE][TRANSACTIONS_COLLECTION]

    query = {"CreatedDateTime": {"$gt": datetime_from}}
    result = collection.find(query).sort("CreatedDateTime", 1)

    for transaction in result:
        yield Transaction(**transaction)
