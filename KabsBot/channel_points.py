# Run: pipenv run python channel_points.py
# Ensure you're in the same directory as this script!

import os
import datetime
import psycopg2

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope
from twitchAPI.pubsub import PubSub
from pprint import pprint
from uuid import UUID


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
    db = None
else:
    print(f"Connected to {os.environ['KABSBOT_DB_NAME']} database.")
finally:
    pass


def send_to_db(reaction, speech):
    global db

    if db:
        sql = f"""INSERT INTO reactions (timestamp, reaction, speech, shown)
                  VALUES ('{datetime.datetime.now()}', '{reaction}', '{speech}', False);"""

        cur = db.cursor()
        cur.execute(sql)
        db.commit()


def callback_channel_point(uuid: UUID, data: dict) -> None:
    print('got callback for UUID ' + str(uuid))
    pprint(data)

    if data['data']['redemption']['reward']['title'] == 'Give Kabs_Bot a coffee':
        display_name = data['data']['redemption']['user']['display_name']
        send_to_db('coffee', f'Thanks for the coffee\n{display_name}!')

def callback_subscription(uuid: UUID, data: dict) -> None:
    print('got callback for UUID ' + str(uuid))
    pprint(data)

    display_name = data['display_name']
    send_to_db('star', f'Thank you for the sub\n{display_name}!')


def callback_bits(uuid: UUID, data: dict) -> None:
    print('got callback for UUID ' + str(uuid))
    pprint(data)



# setting up Authentication and getting your user id
twitch = Twitch(os.environ['REWARD_NEW_CLIENT_ID'], os.environ['REWARD_CLIENT_SECRET'])
target_scope = [AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.BITS_READ]
auth = UserAuthenticator(twitch, target_scope, force_verify=False)
token, refresh_token = auth.authenticate()


# you can get your user auth token and user auth refresh token following the example in twitchAPI.oauth
twitch.set_user_authentication(token, target_scope, refresh_token)

user_id = twitch.get_users(logins=['DNKabs'])['data'][0]['id']
print(f'user_id={user_id} | type = {type(user_id)}')

# starting up PubSub
pubsub = PubSub(twitch)
pubsub.start()
# you can either start listening before or after you started pubsub.
points_uuid = pubsub.listen_channel_points(user_id, callback_channel_point)
subs_uuid = pubsub.listen_channel_subscriptions(user_id, callback_subscription)
bits_uuid = pubsub.listen_bits(user_id, callback_bits)



input('press ENTER to close...\n\n')
# you do not need to unlisten to topics before stopping but you can listen and unlisten at any moment you want
pubsub.unlisten(points_uuid)
pubsub.unlisten(subs_uuid)
pubsub.unlisten(bits_uuid)
pubsub.stop()

if db:
    db.close()
    print(f"Disconnected from {os.environ['KABSBOT_DB_NAME']} database.\n")
