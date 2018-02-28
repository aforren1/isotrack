from transitions import Machine


class StateMachine(Machine):
    def __init__(self):
        states = ['wait',
                  'in_trial',
                  'post_trial',
                  'done']
        
        transitions = [
            {'source': 'wait',
             'trigger': 'step',
             'conditions': 'check_for_space',
             'after': 'remove_text',
             'dest': 'in_trial'},

            {'source': 'in_trial',
             'trigger': 'step',
             'prepare': ['update_target_pos', 'update_target_color_and_count'],
             'conditions': 'samples_exhausted',
             'after': ['draw_time_on_target', 'start_countdown'],
             'dest': 'post_trial'},
            
            {'source': 'post_trial',
             'trigger': 'step',
             'conditions': 'time_elapsed',
             'dest': 'done'}
        ]
        Machine.__init__(self, states=states,
                         transitions=transitions, initial='wait')
