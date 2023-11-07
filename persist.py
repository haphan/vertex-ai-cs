from datetime import datetime
from google.cloud import bigquery
from settings import Settings
from google.cloud._helpers import UTC


settings = Settings()
client = bigquery.Client()
table = client.get_table(settings.bq_table)
client.get_table(settings.bq_table)

def insert_bq(
    session_id: str,
    ask: str,
    response: str,
    dt: datetime,
    ref: str = None
):
    record = {
        'session_id': session_id,
        'datetime': dt.replace(tzinfo=UTC),
        'timestamp':  dt.replace(tzinfo=UTC),
        'ask': ask,
        'response': response,
        'ref': None,
    }

    print('pushing chat record to bq')
    print(record)

    errors = client.insert_rows(table=table, rows=[record])

    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))