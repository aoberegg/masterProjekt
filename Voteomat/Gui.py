"""Written by Dan Kearney, Natalie Mattison, and Theodore Thompson
for Olin College Computational Modeling 2011."""


import pygame
import sys
import matplotlib
from pygame.locals import *
from Slider import *
from Button import *
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as pyplot
matplotlib.rc('xtick', labelsize=2)
matplotlib.rc('ytick', labelsize=2)

class NetworkPanel:
    def __init__(self, width, height):
        self.width = width;
        self.height = height;

class Gui:

    def __init__(self):
        '''graphical representation of the sugarscape object'''
        self.sliders = []
        self.buttons = []
        self.clicked = {}
        pygame.init()
        self.width = 1300
        self.height = 800
        self.started = False
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Voteomat')

        # Fill background
        self.background = pygame.Surface(self.window.get_size())
        self.background = self.background.convert()
        self.background.fill((100, 100, 100))
        self.window.blit(self.background,(0,0))


        pygame.display.set_caption("Voteomat")
        #pygame.draw.rect(self.background, (50,50,75), (10, 10, 70, 70))
        self.draw_buttons()



        while True:
            for event in pygame.event.get():
                self.handle_events(event)
            pygame.display.update()

    def draw_buttons(self):
        Button((self.width-(self.width-100),(self.height-200)), self, 'Start', func = self.start, stay_depressed = True)


    def handle_events(self, event):
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
        if event.type==MOUSEBUTTONDOWN:
            self.handle_click(*event.pos)
        if event.type==MOUSEMOTION:
            self.handle_slider_motion(*event.pos)
        if event.type==MOUSEBUTTONUP:
            self.release_all_sliders()
            self.release_all_buttons()
        return True

    def handle_slider_motion(self, x, y):
        '''handles slider motion'''
        for slider in self.sliders:
            slider.move_slider(x,y)
        return False

    def release_all_sliders(self):
        '''set all sliders to not grabbed'''
        for slider in self.sliders:
            slider.unclick_slider()

    def release_all_buttons(self):
        '''releases all buttons'''
        for button in self.buttons:
            button.unclick_button()

    def handle_click(self,x,y):
        '''handles all possible click events'''
        for slider in self.sliders:
            slider.click_slider(x,y)
        for button in self.buttons:
            button.click_button(x,y)
        return False

    def write_text(self, x, y, text):
        '''writes text on the scape.
        puts a black box behind to erase last text'''
        msg_object = pygame.font.SysFont('verdana', 18).render(text, False, (255,255,255))
        msg_rect = msg_object.get_rect()
        msg_rect.topleft = (x, y)
        pygame.draw.rect(self.window, self.background_color, (0, y, 10000, msg_rect.height))
        self.window.blit(msg_object, msg_rect)


    def start(self):
        self.started = not self.started
        print self.started

if __name__=='__main__':
    Gui();