import datetime
import time

from app.db.mongo_client import get_client
from app.db.operations import (
    get_last_update_datetime,
    get_recent_transaction,
    set_probability_score,
)

client = get_client()


def main() -> None:
    last_checked = get_last_update_datetime(client)

    while True:
        recent_transactions = get_recent_transaction(last_checked, client)

        last_checked = datetime.datetime.now(datetime.UTC)

        for transaction in recent_transactions:
            set_probability_score(transaction, client)

        time.sleep(10)


if __name__ == "__main__":
    main()
