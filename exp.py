from pursuit_imp import Pursuit
from psychopy import core, gui, event

if __name__ == '__main__':
    settings = {'subject': '001',
                'fullscreen': False,
                'mouse': True,
                'trial_table': 'tables/test.csv'}
    dialog = gui.DlgFromDict(dictionary=settings, title='Pursuit')

    if not dialog.OK:
        core.quit()

    # could have a second menu, depending on the experiment
    experiment = Pursuit(settings=settings)

    with experiment.device:
        while experiment.state is not 'done':
            experiment.input()  # collect input
            experiment.draw_input()  # draw the input
            experiment.step()  # evaluate any transitions
            if any(event.getKeys(['escape', 'esc'])):
                experiment.to_done() # bail early
            experiment.win.flip()  # flip frame buffer
    experiment.win.close()
    # experiment.win.saveFrameIntervals() # for debugging
    core.quit()
