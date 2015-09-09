
import gui
from pygame.locals import *
from pygame import font
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
import time



class Gui:

    def __init__(self):
        self.make_new_statistic = True
        self.change = 0
        self.voteomat = Voteomat()
        self.sliders = []
        self.buttons = []
        self.clicked = {}
        self.statistic = None

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

        self.voteomat.candidates[0].orientation = self.voteomat.maxOrientation/2
        self.voteomat.candidates[1].orientation = self.voteomat.minOrientation/2
        self.update_slider()
        self.counterforce_update_slider()
        self.initial_draw_network()
        self.draw_and_save_histogram()
        self.draw_statistic()

        self.draw_settings()

        style = {'font-color': (240,15,15), 'font': font.Font(None,18), 'autosize': True, "antialias": True,
                          'border-width': False, 'border-color': (0,0,0), 'wordwrap': False}
        self.converged_label = gui.Label((self.width-(self.width-50), self.height-20),style = style, parent = self.desktop, text = g_gui_text_converged)
        self.converged_label.visible = False
        while True:

            if self.started:


                self.check_statistic()

                self.update_surface()

                change = self.voteomat.timestep_network_discussion()

                self.timestep += 1

                if not self.change:
                    self.change = change
                else:
                    self.check_converged(change)

            else:
                time.sleep(0.1)

            for e in gui.setEvents(pygame.event.get()):
                self.handle_events(e)
            self.desktop.update()
            self.desktop.draw()

            pygame.display.flip()

    def check_converged(self, change):
        a,b, std = self.voteomat.get_statistic()
        change_of_change = abs(self.change - change)
        if change_of_change < 0.001 or std < .01:
            self.started = False
            self.statistic.network_converged(self.voteomat)
            self.make_new_statistic = True;
            self.converged_label.visible = True
        self.change = change

    def update_surface(self):
        if self.timestep % 5 == 0:
            self.update_drawing()

        self.update_slider()

    def check_statistic(self):
        if self.make_new_statistic:
            self.statistic = Statistic(str(datetime.datetime.now()), self.voteomat)
            self.make_new_statistic = False;

        self.statistic.write_statistic(self.voteomat)


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
        self.write_text(g_gui_right_frame_start+20, 620, g_candidates_affecting_nodes, textsize = 14)
        checkbox_candidates_affecting = gui.CheckBox(position = (g_gui_right_frame_start,620), size = (200,40), value = True, parent = self.desktop, text = "")
        checkbox_candidates_affecting.onValueChanged = self.candidates_affecting_value_changed

    def candidates_affecting_value_changed(self, checkbox_candidates_affecting):
        self.voteomat.candidates_affecting = checkbox_candidates_affecting.value

    def draw_candidates_affected_checkbox(self):
        self.write_text(g_gui_right_frame_start+20, 640, g_candidates_affected_by_median, textsize = 14)
        checkbox_candidates_affected = gui.CheckBox(position = (g_gui_right_frame_start,640), size = (200,40), value = True, parent = self.desktop, text = "")
        checkbox_candidates_affected.onValueChanged = self.candidates_affected_value_changed

    def candidates_affected_value_changed(self, checkbox_candidates_affected):
        self.voteomat.candidates_affected = checkbox_candidates_affected.value

    def draw_neighbour_affecting_checkbox(self):
        self.write_text(g_gui_right_frame_start+20, 660, g_neighbours_affecting_each_other, textsize = 14)
        checkbox_neighbours = gui.CheckBox(position = (g_gui_right_frame_start,660), size = (200,40), value = True, parent = self.desktop, text = "")
        checkbox_neighbours.onValueChanged = self.affecting_neighbours_value_changed

    def affecting_neighbours_value_changed(self, checkbox_neighbours):
        self.voteomat.affecting_neighbours = checkbox_neighbours.value

    def draw_counter_force_affecting_checkbox(self):
        self.write_text(g_gui_right_frame_start+20, 680, g_counterforce_affecting_candidates, textsize = 14)
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
         gui.ListBox(position = (g_gui_right_frame_start +180,480), size = (170, 100),parent = self.desktop,  items =g_networklist)\
                                                        .onItemSelected=self.network_item_selected


    def update_drawing(self):
        self.draw_and_save_network()
        self.draw_statistic()
        self.draw_and_save_histogram()

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

    def counterforce_update_slider(self):
        self.slider3.update_slider(self.voteomat.maxOrientation)
        self.slider4.update_slider(self.voteomat.minOrientation)

    def draw_buttons(self):
        Button((self.width-(self.width-50), (self.height-100)), self, 'Start', width =130, func=self.start, stay_depressed = False)
        Button((self.width-(self.width-190), (self.height-100)), self, 'Stop', width =130, func=self.stop, stay_depressed = False)
        Button((self.width-(self.width-330), (self.height-100)), self, 'Reset', width =130, func=self.reset, stay_depressed = False)
        Button((self.width-(self.width-470), (self.height-100)), self, 'Statistic', width =130, func=self.create_statistic_end, stay_depressed = False)
        Button((self.width-(self.width-610), (self.height-100)), self, 'Load network', width =130, func=self.load_network, stay_depressed = False)
        Button((self.width-(self.width-750), (self.height-100)), self, 'Save network', width =130, func=self.save_network, stay_depressed = False)

    def load_network(self):
        if self.statistic is None:
            self.statistic = Statistic(str(datetime.datetime.now()), self.voteomat)
            self.make_new_statistic = False
        G = self.statistic.load_network_from_file()
        if G is not None:
            self.voteomat.set_network(G)
            self.pos = networkx.spring_layout(G, iterations=100)
            self.update_drawing()

    def save_network(self):
        if self.statistic is None:
            self.statistic = Statistic(str(datetime.datetime.now()), self.voteomat)
            self.make_new_statistic = False
        self.statistic.save_network_in_file(self.voteomat.get_network(), self.timestep)
    def create_statistic_end(self):
        self.started = False
        if self.statistic is not None:
            self.statistic.network_converged(self.voteomat)
        self.make_new_statistic = True;
        self.reset()

    def draw_slider(self):
        self.slider1 = Slider((self.width-(self.width-50), (self.height-250)), "Political Orientation candidate 1", self,
               self.adjust_candidate1_orientation, self.voteomat.candidates[0].orientation, 50, -50)

        self.slider2 = Slider((self.width-(self.width-400), (self.height-250)), "Political Orientation candidate 2", self,
               self.adjust_candidate2_orientation, self.voteomat.candidates[1].orientation, 50, -50)

        self.slider3 = Slider((self.width-(self.width-50), (self.height-150)), "Counter force candidate 1", self,
           self.adjust_counterforce_left, self.voteomat.counter_force_left, 50, -50)

        self.slider4 = Slider((self.width-(self.width-400), (self.height-150)), "Counter force candidate 2", self,
           self.adjust_counterforce_right, self.voteomat.counter_force_right, 50, -50)


    def adjust_candidate1_orientation(self, new_value, from_move):

        self.voteomat.set_orientation_candidate(0,new_value, not from_move)

    def adjust_candidate2_orientation(self, new_value, from_move):
        self.voteomat.set_orientation_candidate(1,new_value, not from_move)

    def adjust_counterforce_left(self, new_value, from_move):
        self.voteomat.counter_force_left = new_value

    def adjust_counterforce_right(self, new_value, from_move):
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

    def draw_and_save_histogram(self):
        G = self.voteomat.get_network()
        orientation_list = []
        for node in G.nodes(data=True):
            orientation_list.append(int(node[1]["orientation"]))

        fig = plt.figure(1, figsize=(4, 4))
        self.ax = fig.gca()
        self.ax.hist(orientation_list, 20, normed=False)
        plt.xlabel("Orientation")
        plt.ylabel("#Nodes")
        plt.suptitle("Voting distribution")

        self.canvas = agg.FigureCanvasAgg(fig)
        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        self.network_screen = pygame.display.get_surface()
        self.canvas_width_height = self.canvas.get_width_height()
        surf = pygame.image.fromstring(raw_data, self.canvas_width_height, "RGB")
        self.network_screen.blit(surf, (g_gui_right_frame_start, g_gui_top_space))
        if not self.make_new_statistic:
            self.statistic.save_histogram(fig, self.timestep)
        plt.close()

    def draw_and_save_network(self):
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
        if not self.make_new_statistic:
            self.statistic.save_network(fig, self.timestep)
            self.statistic.save_network_in_file(self.voteomat.get_network(), self.timestep)
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

    def write_text(self, x, y, text, textsize = 14, color = (255,255,255)):
        msg_object = pygame.font.SysFont('verdana', textsize).render(text, False, color)
        msg_rect = msg_object.get_rect()
        msg_rect.topleft = (x, y)
        pygame.draw.rect(self.window, self.background_color, (x, y, 10000, msg_rect.height))
        self.window.blit(msg_object, msg_rect)

    def start(self):
        self.started = True

    def stop(self):
        self.started = False;

    def reset(self):
        self.voteomat.reset()
        self.timestep = 0
        self.initial_draw_network()
        self.make_new_statistic = True
        self.converged_label.visible = False
        self.desktop.update()
        self.desktop.draw()
        self.update_slider()
        self.draw_and_save_histogram()
        self.draw_statistic()
        pygame.display.flip()

if __name__=='__main__':
    Gui()