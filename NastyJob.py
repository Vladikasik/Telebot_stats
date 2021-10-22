import time

class MsgDecoder:

    def __init__(self):
        pass

    def get_start(self, msg):
        user_id = msg.from_user.id
        try:
            start_code = msg.text.split(' ')[1]
        except IndexError:
            start_code = 0
        return user_id, start_code, time.time()
    
    def get_action(self, action, typeof):
        if typeof == 'msg':
            action_id = action.id
            action_type = "message"
            action_text = action.text
            action_command = ""
            from_user_id = action.from_user.id
            action_date = time.time()
            is_start = True if action_text.startswith('/start') else False
            values = (action_id, action_type, action_text,
                    action_command, from_user_id, action_date, is_start)
            return action_text, from_user_id, action_date, is_start, values
        elif typeof == 'callback':
            action_id = action.id
            action_type = "callback"
            action_text = action.message.json['reply_markup']['inline_keyboard'][0][0]['text']
            action_command = action.message.json['reply_markup']['inline_keyboard'][0][0]['callback_data']
            from_user_id = action.from_user.id
            action_date = time.time()
            is_start = False
            values = (action_id, action_type, action_text,
                    action_command, from_user_id, action_date, is_start)
            return action_text, from_user_id, action_date, values