import os
import psycopg2
import argparse
import datetime

parser = argparse.ArgumentParser(prog="reactions_db", description="Send data for Kabs_Bot to react on-stream")
parser.add_argument("reaction", help="Kabs_Bot reaction animation", type=str)
parser.add_argument("line1", help="First line of Kabs_Bot reaction text", type=str)
parser.add_argument("line2", help="Second line of Kabs_Bot reaction text", type=str, default="")
args = parser.parse_args()

speech = args.line1 + "\n" + args.line2

try:
    db = psycopg2.connect(
            database=os.environ['KABSBOT_DB_NAME'],
            user=os.environ['KABSBOT_DB_USER'],
            password=os.environ['KABSBOT_DB_PASSWORD'],
            host=os.environ['KABSBOT_DB_HOST'],
            port=os.environ['KABSBOT_DB_PORT']
    )
except Exception as e:
    print("Could not connect to database!")
    print(str(e))
else:
    print(f"Connected to {os.environ['KABSBOT_DB_NAME']} database.\n")
    sql = f"""INSERT INTO reactions (timestamp, reaction, speech, shown)
                  VALUES ('{datetime.datetime.now()}', '{args.reaction}', '{speech}', False);"""

    cur = db.cursor()
    cur.execute(sql)
    db.commit()

    print(f"Sent \"{args.reaction}\" reaction to db, with text:\n" + speech + "\n")
finally:
    db.close()
    print(f"Disconnected from {os.environ['KABSBOT_DB_NAME']} database.\n")
