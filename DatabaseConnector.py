import sqlite3
import time
from NastyJob import MsgDecoder


class DbConnector:

    def __init__(self):
        self.decoder = MsgDecoder()
        self.conn = None
        self.cur = None

    def _new_start(self, msg):

        self.conn = sqlite3.connect('db.sqlite')
        self.cur = self.conn.cursor()

        user_id, start_code, timeof = self.decoder.get_start(msg)

        self.cur.execute('select * from "Users" where user_id=:id_given', {'id_given': user_id})
        ans = self.cur.fetchone()
        if not ans:
            self.cur.execute('''insert into "Users" 
                            (user_id,
                             code_from_start, 
                             msg_amount_received_from_bot, 
                             msg_amount_sent_to_bot, 
                             last_msg_sfb, last_msg_stb, 
                             last_time_sfb, last_time_stb, 
                             bot_blocked_by_user) 
                             values 
                             (:id_given, 
                             :start_code_given,
                             0,
                             1,
                             "",
                             "/start",
                             0,
                             :timestamp,
                             false)''', {'id_given': user_id,
                                         'start_code_given': start_code,
                                         'timestamp': timeof})
            self.conn.commit()
            self.conn.close()
            print('User was succesfully added to db')
            return 1
        else:
            print('User already exists in db\n'
            '(it meands this user pressed /start 2nd time)')
            return 0

    def any_action(self, action, action_type_query, user_id, with_start=False):
        self.conn = sqlite3.connect('db.sqlite')
        self.cur = self.conn.cursor()
        if action_type_query == 'msg':
            # decoding all data from message body
            # first going separrate values, then all-in-one values for sql
            action_text, user_id, timeof, is_start, values = self.decoder.get_action(action)
            self.cur.execute('''insert into "Actions"
                                (action_id, action_type,
                                action_text, action_command,
                                from_user_id, action_date,
                                is_start)
                                values (?, ?, ?, ?, ?, ?, ?)''', values)
            if is_start:
                self._new_start()
            else:
                self.cur.execute('''update "Users" set 
                                    last_msg_stb = ?,
                                    last_time_stb = ?,
                                    msg_amount_sent_to_bot = msg_amount_sent_to_bot + 1
                                    where user_id = ?''', (action_text, timeof, user_id))
            self.conn.commit()
            self.cur.close()
            return 1
        elif action_type_query == 'callback':
            pass  # todo watch how to get a text from callback
    
    def bot_message(self, msg, to_user_id):
        pass