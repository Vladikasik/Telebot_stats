import sqlite3
import time


class DbConnector:

    def __init__(self):
        self.conn = None
        self.cur = None

    def _new_start(self, msg):

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
            # noinspection SqlResolve
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
                                         'timestamp': time.time()})
            self.conn.commit()
            self.conn.close()
            return 1
        else:
            return 0

    def any_action(self, action, action_type_query, user_id, with_start=False):
        self.conn = sqlite3.connect('db.sqlite')
        self.cur = self.conn.cursor()
        if action_type_query == 'msg':
            action_id = action.id
            action_type = "message"
            action_text = action.text
            action_command = False
            from_user_id = action.from_user.id
            action_date = time.time()
            is_start = True if action_text.startswith('/start') else False
            values = (action_id, action_type, action_type, action_text,
                      action_command, from_user_id, action_date, is_start)
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
                                    where user_id = ?''', (action_text, time.time(), from_user_id))
            return 1
        elif action_type_query == 'callback':
            pass  # todo watch how to get a text from callback
