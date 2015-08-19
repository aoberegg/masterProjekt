import gui
from pygame.locals import *
import datetime
from Statistic import *

from Slider import *
from Button import *

from Voteomat import Voteomat

import networkx
from networkx import *
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
from Globals import *
import defaultStyle


class Gui:

    def __init__(self):
        self.voteomat = Voteomat()
        self.sliders = []
        self.buttons = []
        self.clicked = {}

        self.width = g_gui_width
        self.height = g_gui_height
        self.started = False
        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Voteomat')

        # Fill background
        self.background = pygame.Surface(self.window.get_size())
        self.background = self.background.convert()
        self.background_color = g_gui_background
        self.background.fill(self.background_color)
        self.window.blit(self.background, (0, 0))

        # Draw Buttons and Network
        self.write_text(self.width/2, 10, g_gui_heading)
        self.timestep = 0
        self.draw_buttons()
        self.draw_slider()

        self.voteomat.set_orientation_candidate(0, self.voteomat.maxOrientation/2)
        self.voteomat.set_orientation_candidate(1, self.voteomat.minOrientation/2)
        self.update_slider()
        self.initial_draw_network()
        self.draw_histogram()
        self.draw_statistic()

        self.draw_settings()

        self.make_new_statistic = True
        while True:
            if self.started:
                if self.make_new_statistic:
                    self.statistic = Statistic(str(datetime.datetime.now()), self.voteomat)
                    self.make_new_statistic = False;
                self.update_network()
                if self.timestep % 5 == 0:
                    self.update_drawing()
                self.statistic.writestatistic(self.voteomat)
                self.timestep += 1
                self.update_slider()

            for e in gui.setEvents(pygame.event.get()):
                self.handle_events(e)
            self.desktop.update()
            self.desktop.draw()

            pygame.display.flip()

    def draw_settings(self):
        defaultStyle.init(gui)
        self.desktop = gui.Desktop()
        self.desktop.surf = self.window
        self.draw_distribution_listbox()
        self.draw_network_listbox()
        self.draw_acceptance_text_box()
        self.draw_neighbour_affecting_checkbox()
        self.draw_candidates_affecting_checkbox()
        self.draw_candidates_affected_checkbox()
        self.draw_counter_force_affecting_checkbox()

    def draw_candidates_affecting_checkbox(self):
        self.write_text(g_gui_right_frame_start+20, 620, "Candidates affecting nodes", textsize = 14)
        checkbox_candidates_affecting = gui.CheckBox(position = (g_gui_right_frame_start,620), size = (200,40), value = True, parent = self.desktop, text = "")
        checkbox_candidates_affecting.onValueChanged = self.candidates_affecting_value_changed

    def candidates_affecting_value_changed(self, checkbox_candidates_affecting):
        self.voteomat.candidates_affecting = checkbox_candidates_affecting.value

    def draw_candidates_affected_checkbox(self):
        self.write_text(g_gui_right_frame_start+20, 640, "Candidates get affected by median node", textsize = 14)
        checkbox_candidates_affected = gui.CheckBox(position = (g_gui_right_frame_start,640), size = (200,40), value = True, parent = self.desktop, text = "")
        checkbox_candidates_affected.onValueChanged = self.candidates_affected_value_changed

    def candidates_affected_value_changed(self, checkbox_candidates_affected):
        self.voteomat.candidates_affected = checkbox_candidates_affected.value

    def draw_neighbour_affecting_checkbox(self):
        self.write_text(g_gui_right_frame_start+20, 660, "Neighbours affecting each other", textsize = 14)
        checkbox_neighbours = gui.CheckBox(position = (g_gui_right_frame_start,660), size = (200,40), value = True, parent = self.desktop, text = "")
        checkbox_neighbours.onValueChanged = self.affecting_neighbours_value_changed

    def affecting_neighbours_value_changed(self, checkbox_neighbours):
        self.voteomat.affecting_neighbours = checkbox_neighbours.value

    def draw_counter_force_affecting_checkbox(self):
        self.write_text(g_gui_right_frame_start+20, 680, "Counterforce affecting candidates", textsize = 14)
        checkbox_counterforce_affecting = gui.CheckBox(position = (g_gui_right_frame_start,680), size = (200,40), value = True, parent = self.desktop, text = "")
        checkbox_counterforce_affecting.onValueChanged = self.counterforce_affecting_value_changed

    def counterforce_affecting_value_changed(self, checkbox_counterforce_affecting):
        self.voteomat.counter_force_affecting = checkbox_counterforce_affecting.value

    def draw_acceptance_text_box(self):
        self.write_text(g_gui_right_frame_start, 590, "Acceptance: ")
        gui.TextBox(position = (g_gui_right_frame_start+100,590), size = (100,20), parent = self.desktop, text = str(self.voteomat.acceptance)).onMouseLeave = self.set_acceptance

    def set_acceptance(self, widget):
        self.voteomat.set_acceptance(round(float(widget.text),2))

    def draw_distribution_listbox(self):
        gui.ListBox(position = (g_gui_right_frame_start,480), size = (170, 100),parent = self.desktop,  items =[g_uniform_distribution,
                                                        g_normal_distribution_left, g_normal_distribution_right,
                                                        g_normal_distribution_avg, g_normal_left_and_right])\
                                                        .onItemSelected=self.distribution_item_selected
    def draw_network_listbox(self):
         gui.ListBox(position = (g_gui_right_frame_start +180,480), size = (170, 100),parent = self.desktop,  items =[g_newman_watts_strogats,
                                                        g_random_regular, g_barabasi_albert,
                                                        g_random_powerlaw_tree])\
                                                        .onItemSelected=self.network_item_selected

    def update_network(self):
        self.voteomat.timestep_network_discussion()

    def update_drawing(self):
        self.draw_network()
        self.draw_statistic()
        self.draw_histogram()

    def network_item_selected(self, widget):
        if widget.selectedIndex < len(widget.items):
            self.voteomat.set_network_func(str(widget.items[widget.selectedIndex]))
            self.update_drawing()

    def distribution_item_selected(self, widget):
        if widget.selectedIndex < len(widget.items):
            self.voteomat.set_distribution_func(str(widget.items[widget.selectedIndex]))
            self.update_drawing()


    def draw_statistic(self):
        y = 370
        median, avg, std = self.voteomat.get_statistic()
        self.write_text(g_gui_right_frame_start, y, "Timestep: " + str(round(self.timestep,2)))
        self.write_text(g_gui_right_frame_start, y+20, "Median: "+str(round(median, 2)))
        self.write_text(g_gui_right_frame_start, y+40, "Avg.:   " + str(round(avg, 2)))
        self.write_text(g_gui_right_frame_start, y+60, "#Voter:  " + str(round(self.voteomat.get_amount_voter(), 2)))
        self.write_text(g_gui_right_frame_start, y+80, "Standard deviation: " + str(round(std, 2)))

    def update_slider(self):
        self.slider1.update_slider(self.voteomat.candidates[0].orientation)
        self.slider2.update_slider(self.voteomat.candidates[1].orientation)

    def draw_buttons(self):
        Button((self.width-(self.width-50), (self.height-100)), self, 'Start', func=self.start, stay_depressed = True)
        Button((self.width-(self.width-180), (self.height-100)), self, 'Reset', func=self.reset, stay_depressed = False)

    def draw_slider(self):
        self.slider1 = Slider((self.width-(self.width-50), (self.height-250)), "Political Orientation candidate 1", self,
               self.adjust_candidate1_orientation, self.voteomat.candidates[0].orientation, 50, -50)

        self.slider2 = Slider((self.width-(self.width-400), (self.height-250)), "Political Orientation candidate 2", self,
               self.adjust_candidate2_orientation, self.voteomat.candidates[1].orientation, 50, -50)

        self.slider3 = Slider((self.width-(self.width-50), (self.height-150)), "Counter force candidate 1", self,
           self.adjust_counterforce_left, self.voteomat.counter_force_left, 50, -50)

        self.slider4 = Slider((self.width-(self.width-400), (self.height-150)), "Counter force candidate 2", self,
           self.adjust_counterforce_right, self.voteomat.counter_force_right, 50, -50)


    def adjust_candidate1_orientation(self, new_value):
        self.voteomat.set_orientation_candidate(0,new_value)

    def adjust_candidate2_orientation(self, new_value):
        self.voteomat.set_orientation_candidate(1,new_value)

    def adjust_counterforce_left(self, new_value):
        self.voteomat.counter_force_left = new_value

    def adjust_counterforce_right(self, new_value):
        self.voteomat.counter_force_right = new_value

    def get_node_color(self, G):
        node_color = []
        max_value = self.voteomat.maxOrientation
        color_threshold = 0.2
        for node in G.nodes(data=True):
            if node[1]["orientation"] > 0:
                value = node[1]["orientation"]/max_value;
                value = 1 - value
                node_color.append((0, 0, value if value > color_threshold else color_threshold))
            else:
                value = (node[1]["orientation"]+max_value)/max_value
                node_color.append((0, value if value > color_threshold else color_threshold, 0))
        return node_color

    def draw_histogram(self):
        G = self.voteomat.get_network()
        orientation_list = []
        for node in G.nodes(data=True):
            orientation_list.append(int(node[1]["orientation"]))

        fig = plt.figure(1, figsize=(4, 4))
        self.ax = fig.gca()
        self.ax.hist(orientation_list, 20, normed=False)
        plt.suptitle("Voting distribution")

        self.canvas = agg.FigureCanvasAgg(fig)
        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        self.network_screen = pygame.display.get_surface()
        self.canvas_width_height = self.canvas.get_width_height()
        surf = pygame.image.fromstring(raw_data, self.canvas_width_height, "RGB")
        self.network_screen.blit(surf, (g_gui_right_frame_start, g_gui_top_space))
        plt.close()

    def draw_network(self):
        G = self.voteomat.get_network()
        fig = plt.figure(1, figsize=(12, 7))
        networkx.draw(G, self.pos, node_color=self.get_node_color(G))
        self.ax = fig.gca()
        self.canvas = agg.FigureCanvasAgg(fig)
        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        self.network_screen = pygame.display.get_surface()
        self.canvas_width_height = self.canvas.get_width_height()
        surf = pygame.image.fromstring(raw_data, self.canvas_width_height, "RGB")
        self.network_screen.blit(surf, (g_gui_left_frame_start, g_gui_top_space))
        plt.close()

    def initial_draw_network(self):
        G = self.voteomat.get_network()
        self.pos = networkx.spring_layout(G, iterations=100)
        fig = plt.figure(1, figsize=(12, 7))
        networkx.draw(G, self.pos, node_color=self.get_node_color(G))
        self.ax = fig.gca()
        self.canvas = agg.FigureCanvasAgg(fig)
        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        self.network_screen = pygame.display.get_surface()
        self.canvas_width_height = self.canvas.get_width_height()
        surf = pygame.image.fromstring(raw_data, self.canvas_width_height, "RGB")
        self.network_screen.blit(surf, (g_gui_left_frame_start, g_gui_top_space))
        plt.close()

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
        for slider in self.sliders:
            slider.move_slider(x,y)
        return False

    def release_all_sliders(self):
        for slider in self.sliders:
            slider.unclick_slider()

    def release_all_buttons(self):
        for button in self.buttons:
            button.unclick_button()

    def handle_click(self,x,y):
        for slider in self.sliders:
            slider.click_slider(x,y)
        for button in self.buttons:
            button.click_button(x,y)
        return False

    def write_text(self, x, y, text, textsize = 14):
        msg_object = pygame.font.SysFont('verdana', textsize).render(text, False, (255,255,255))
        msg_rect = msg_object.get_rect()
        msg_rect.topleft = (x, y)
        pygame.draw.rect(self.window, self.background_color, (x, y, 10000, msg_rect.height))
        self.window.blit(msg_object, msg_rect)

    def start(self):
        self.started = not self.started

    def reset(self):
        self.voteomat.reset()
        self.timestep = 0
        self.initial_draw_network()
        self.draw_histogram()
        self.draw_statistic()
        self.make_new_statistic = True
        pygame.display.flip()

if __name__=='__main__':
    Gui()