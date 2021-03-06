import sqlite3
import time
from NastyJob import MsgDecoder


class DbConnector:

    def __init__(self):
        self.decoder = MsgDecoder()
        self.conn = None
        self.cur = None

    def _new_start(self, msg):
        self._connect()

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
            self._disconnect()
            print('User was succesfully added to db')
            return 1
        else:
            print('User already exists in db\n'
            '(it meands this user pressed /start 2nd time)')
            return 0

    def any_action(self, action, action_type_query, with_start=False):
        self._connect()
        if action_type_query == 'msg':
            # decoding all data from message body
            # first going separrate values, then all-in-one values for sql
            action_text, user_id, timeof, is_start, values = self.decoder.get_action(action, 'msg')
            self.cur.execute('''insert into "Actions"
                                (action_id, action_type,
                                action_text, action_command,
                                from_user_id, action_date,
                                is_start)
                                values (?, ?, ?, ?, ?, ?, ?)''', values)
            if self._new_start(action):
                self.cur.execute('''update "Users" set 
                                    last_msg_stb = ?,
                                    last_time_stb = ?,
                                    msg_amount_sent_to_bot = msg_amount_sent_to_bot + 1
                                    where user_id = ?''', (action_text, timeof, user_id))
            self._disconnect()
            return 1
        elif action_type_query == 'callback':
            action_text, from_user_id, timeof, values = self.decoder.get_action(action, 'callback')
            self.cur.execute('''insert into "Actions"
                                (action_id, action_type,
                                action_text, action_command,
                                from_user_id, action_date,
                                is_start)
                                values (?, ?, ?, ?, ?, ?, ?)''', values)

            self.cur.execute('''update "Users" set
                                last_command_text = ?,
                                last_command_time = ?,
                                command_amount_sent_to_bot = command_amount_sent_to_bot + 1
                                where user_id = ?''', (action_text, timeof, from_user_id))
            self._disconnect()
        
        def message_from_bot(self, msg):
            self._connect()
            try: # if somehow function was runned bufore creation of user
                self.cur.execute('''update "Users" set
                                    msg_amount_received_from_bot = msg_amount_received_from_bot + 1,
                                    last_msg_sfb = ?,
                                    last_time_sfb = ?
                                    where user_id = ?''', (msg.text, time.time(), msg.chat.id))
                self._disconnect()
            except Exception as e:
                print('Probably you called this func before user was created in db\n'
                'Actual problem:',
                e, sep='\n')

        
        def _connect(self):
            self.conn = sqlite3.connect('db.sqlite')
            self.cur = self.conn.cursor()
        
        def _disconnect(self):
            self.cur.commit()
            self.conn.close()

    def bot_message(self, msg, to_user_id):
        pass