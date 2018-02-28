import numpy as np
import pandas as pd
from psychopy import core, event, visual, logging

from toon.input import MultiprocessInput
from toon.input.clock import mono_clock
from state_dec import StateMachine
from sham_mouse import Mouse

class Pursuit(StateMachine):
    def __init__(self, settings=None):
        super(Pursuit, self).__init__()
        self.global_clock = mono_clock

        # set up input
        if settings['mouse']:
            self.device = Mouse(clock=self.global_clock.getTime)
        else:
            core.quit()
            #self.device = ForceHandle(clock=self.global_clock.getTime)
        try:
            #self.trial_table = pd.read_csv(settings['trial_table'])
            pass
        except FileNotFoundError:
            core.quit()
        
        # set up display
        self.win = visual.Window(size=(800, 800),
                                 pos=(0, 0),
                                 fullscr=settings['fullscreen'],
                                 screen=1,
                                 units='height',
                                 allowGUI=False,
                                 colorSpace='rgb',
                                 color=(-1, -1, -1))
        self.win.recordFrameIntervals = True

        self.setup_visuals()

        # extras
        self.data = None
        self.total_frames = 0
        self.frames_on_target = 0
    
    def setup_visuals(self):
        self.target = visual.Circle(self.win, size=0.05, fillColor=[0, 0, 0],
                                    pos=(0, 0), autoDraw=True, autoLog=False,
                                    name='target')
        self.player = visual.Circle(self.win, size=0.025, fillColor=[1, 1, 1],
                                    pos=(0, 0), autoDraw=True, autoLog=False,
                                    name='player')
        self.post_text = visual.TextStim(self.win, text='Spacebar to start.',
                                         pos=(0, 0.4), units='height',
                                         color=[1, 1, 1],
                                         height=0.1,
                                         alignHoriz='center', alignVert='center',
                                         name='post_text', autoLog=False,
                                         wrapWidth=2)
        self.post_text.autoDraw = True

    def check_for_space(self):
        return any(event.getKeys(['space', 'spacebar']))
    
    def remove_text(self):
        self.post_text.autoDraw = False
    
    def update_target_pos(self):
        self.target.pos = [np.sin(self.total_frames/50.0)/3.5, 
                           np.cos(self.total_frames/100.0)/4.0]
    
    def update_target_color_and_count(self):
        self.total_frames += 1
        if self.player.contains(self.target.pos):
            self.frames_on_target += 1
            self.target.fillColor = [-0.2, 0.8, -0.1]
        else:
            self.target.fillColor = [0, 0, 0]
    
    def samples_exhausted(self):
        return self.total_frames > 500
    
    def draw_time_on_target(self):
        self.post_text.setText('Percentage: ' + str(round(100*(self.frames_on_target/self.total_frames), 0)))
        self.post_text.autoDraw = True
    
    def start_countdown(self):
        self.countdown_timer = core.CountdownTimer(5)
    
    def time_elapsed(self):
        return self.countdown_timer.getTime() <= 0
    
    def input(self):
        timestamp, self.data = self.device.read()
    
    def draw_input(self):
        self.player.pos = self.data
