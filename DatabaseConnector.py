import sqlite3
import time


class DbConnector:

    def __init__(self):
        self.conn = None
        self.cur = None

    def new_start(self, msg):

        self.conn = sqlite3.connect('db.sqlite')
        self.cur = self.conn.cursor()

        user_id = msg.from_user.id
        try:
            start_code = msg.text.split(' ')[1]
        except IndexError:
            start_code = 0

        self.cur.execute('select * from "Users" where user_id=:id_given', {'id_given': user_id})
        ans = self.cur.fetchone()
        if not ans:
            self.cur.execute('insert into "Users" (user_id, '
                             'code_from_start, '
                             'msg_amount_received_from_bot, '
                             'msg_amount_sent_to_bot, '
                             'last_msg_sfb, last_msg_stb, '
                             'last_time_sfb, las_time_stb, '
                             'bot_blocked_by_user) values '
                             '(:id_given, '
                             ':start_code_given,'
                             '0,'
                             '1,'
                             '"",'
                             '"/start",'
                             '0,'
                             ':timestamp,'
                             'false)', {'id_given': user_id,
                                        'start_code_given': start_code,
                                        'timestamp': time.time()})
            self.conn.commit()
            return 1
        else:
            return 0

    def any_action(self, with_start=False, action_type, user_id):
        pass

