import os   
import tkinter as tk 

import random

from PyAstronomy import pyasl

import matplotlib
matplotlib.use('tkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt

import pandas as pd

import user_settings
import synthe

font = ("Courier", 14)

global_center = user_settings.XCENTER

class tkinterApp(tk.Tk): 
    def __init__(self, *args, **kwargs):  
        tk.Tk.__init__(self, *args, **kwargs) 

        self.current_model = None
        self.current_spec = None
        self.current_list_pos = None

        if user_settings.CACHE_LAST:
            if os.path.exists('last_star'):
                with open('last_star', 'r') as f:
                    lines = f.readlines()
                self.current_model = lines[0][:-1]
                self.current_spec = lines[1][:-1]
                if len(lines) == 3:
                    self.current_list_pos = int(lines[2][:-1])

        container = tk.Frame(self)   
        container.pack(side = "top", fill = "both", expand = True)  
   
        container.grid_rowconfigure(0, weight = 1) 
        container.grid_columnconfigure(0, weight = 1) 

        self.frames = {}   
   
        for F in (InputPage, FitPage, ParamsPage): 
            frame = F(container, self) 
            self.frames[F] = frame  
   
            frame.grid(row = 0, column = 0, sticky ="nsew") 
   
        self.show_frame(ParamsPage) 
        if self.current_model and self.current_spec:
            self.draw_new()

    def show_frame(self, cont): 
        frame = self.frames[cont] 
        frame.tkraise() 
    
    def draw_new(self):
        self.frames[FitPage].draw_new(self)
        if user_settings.CACHE_LAST:
            with open('last_star', 'w') as f:
                f.writelines([
                    self.current_model + '\n',
                    self.current_spec + '\n',
                ])

    def update(self):
        self.frames[FitPage].limupdate('')
        self.frames[FitPage].synupdate()

    def get_log_entry(self):
        return self.frames[ParamsPage].current_params() + f',{self.frames[FitPage].s_deltasyn_x.val},{self.frames[FitPage].s_deltasyn_y.val}'

'''
    Text input page. Used for manually setting the current star's spectrum and model.
'''
class InputPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(controller, width=700, height=100,  relief='raised')
        self.canvas.pack()

        label_mod = tk.Label(controller, text='Path to model:')
        self.canvas.create_window(70, 25, window=label_mod)
        self.entry_model = tk.Entry(controller, width=30)
        self.canvas.create_window(250, 25, window=self.entry_model)

        label_spec = tk.Label(controller, text='Path to spectrum:')        
        self.canvas.create_window(70, 50, window=label_spec)
        self.entry_spec = tk.Entry(controller, width=30)
        self.canvas.create_window(250, 50, window=self.entry_spec)
        
        button_open = tk.Button(text='Open', command=lambda: self.load_inputs(controller))
        self.canvas.create_window(300, 75, window=button_open)

        button_clear = tk.Button(text='Clear', command=self.clear_text)
        self.canvas.create_window(230, 75, window=button_clear)

        button_save = tk.Button(text='Save to log', command=lambda: self.save_current_fit(controller))
        self.canvas.create_window(450, 50, window=button_save)

        button_next = tk.Button(text='Next (list)', command=lambda: self.next_in_list(controller, save=False))
        self.canvas.create_window(600, 80, window=button_next)
        
        button_next_save = tk.Button(text='Save and next', command=lambda: self.next_in_list(controller, save=True))
        self.canvas.create_window(600, 50, window=button_next_save)

        if controller.current_model and controller.current_spec:
            self.entry_update(controller)

        self.list_pos = controller.current_list_pos
        self.input_list = None
        if user_settings.INPUT_LIST_PATH:
            with open(user_settings.INPUT_LIST_PATH, 'r') as f:
                self.input_list = f.readlines() 

    def load_inputs(self, controller):
        controller.current_model = self.entry_model.get()
        controller.current_spec = self.entry_spec.get()
        controller.draw_new()

    def clear_text(self):
        self.entry_spec.delete(0, tk.END)
        self.entry_model.delete(0, tk.END)
    
    @staticmethod
    def set_text(entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def entry_update(self, controller):
        self.set_text(self.entry_model, controller.current_model)
        self.set_text(self.entry_spec, controller.current_spec)

    def save_current_fit(self, controller):
        if not os.path.exists(user_settings.OUTPUT_LOG_DIR + 'intsyn.log'):
            with open(user_settings.OUTPUT_LOG_DIR + 'intsyn.log', 'w') as f:
                f.write('element,center,spec_file,vmac,vrot,resolution,abn,offset_x,offset_y\n')
        with open(user_settings.OUTPUT_LOG_DIR + 'intsyn.log', 'a') as f:
            f.write(f'{user_settings.ELEMENT},{global_center},{controller.current_spec},{controller.get_log_entry()}\n')
        if user_settings.SAVE_SYNTHETIC_SPECTRA:
            os.system(f"cp synthe/br.dat out/{controller.current_spec.split('.')[0] + str(global_center) + '.dat'}")

    def next_in_list(self, controller, save):
        if save:
            self.save_current_fit(controller)
            if user_settings.SHORTEN_LIST:
                if not os.path.exists(user_settings.SHORT_LIST_PATH):
                    os.system(f'cp {user_settings.INPUT_LIST_PATH} {user_settings.SHORT_LIST_PATH}')
                with open(user_settings.SHORT_LIST_PATH, 'r') as f:
                    lines = f.readlines()
                with open(user_settings.SHORT_LIST_PATH, 'w') as f:
                    if self.list_pos:
                        lines.remove(self.input_list[self.list_pos])
                    f.writelines(lines)

        if self.list_pos is None:
            self.list_pos = 0
        else:
            self.list_pos += 1
        if len(self.input_list) >= (self.list_pos + 1):
            list_line = self.input_list[self.list_pos].replace('\n', '').split(',')
            controller.current_model = list_line[0]
            controller.current_spec = list_line[1]
            self.entry_update(controller)
            print(f'{self.list_pos + 1}/{len(self.input_list)}')
            controller.draw_new()
            if user_settings.CACHE_LAST:
                with open('last_star', 'a') as f:
                    f.write(f'{self.list_pos}\n')
        else:
            print('List finished')
            quit()


class ParamsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.params = user_settings.DEFAULT_PARAMS
        self.abn = user_settings.DEFAULT_PARAMS['abn']
        self.elmt = user_settings.ELEMENT
        self.center = global_center
        
        self.canvas = tk.Canvas(controller, width=700, height=100,  relief='raised')
        self.canvas.pack()

        label_vmac = tk.Label(controller, text='VMAC:')
        self.canvas.create_window(50, 25, window=label_vmac)
        self.entry_vmac = tk.Entry(controller)
        self.canvas.create_window(150, 25, window=self.entry_vmac)
        self.slider_vmac = tk.Scale(controller, 
            from_=float(self.params['vmac'])-user_settings.PARAM_BOUNDARIES['vmac'], 
            to=float(self.params['vmac'])+user_settings.PARAM_BOUNDARIES['vmac'],
            length=250, width=10,
            resolution=0.01,
            command=lambda t: self.set_text(self.entry_vmac, t),
            orient=tk.HORIZONTAL)
        self.slider_vmac.set(float(self.params['vmac']))
        self.canvas.create_window(400, 20, window=self.slider_vmac)

        label_vrot = tk.Label(controller, text='VROT:')        
        self.canvas.create_window(50, 50, window=label_vrot)
        self.entry_vrot = tk.Entry(controller)
        self.canvas.create_window(150, 50, window=self.entry_vrot)
        self.slider_vrot = tk.Scale(controller, 
            from_=float(self.params['vrot'])-user_settings.PARAM_BOUNDARIES['vrot'], 
            to=float(self.params['vrot'])+user_settings.PARAM_BOUNDARIES['vrot'],
            length=250, width=10,
            resolution=0.01,
            command=lambda t: self.set_text(self.entry_vrot, t),
            orient=tk.HORIZONTAL)
        self.slider_vrot.set(float(self.params['vrot']))
        self.canvas.create_window(400, 45, window=self.slider_vrot)

        label_abn = tk.Label(controller, text='A(X):')        
        self.canvas.create_window(50, 75, window=label_abn)
        self.entry_abn = tk.Entry(controller)
        self.canvas.create_window(150, 75, window=self.entry_abn)
        self.slider_abn = tk.Scale(controller, 
            from_=float(self.params['abn'])-user_settings.PARAM_BOUNDARIES['abn'], 
            to=float(self.params['abn'])+user_settings.PARAM_BOUNDARIES['abn'],
            length=250, width=10,
            resolution=0.01,
            command=lambda t: self.set_text(self.entry_abn, t),
            orient=tk.HORIZONTAL)
        self.slider_abn.set(float(self.params['abn']))
        self.canvas.create_window(400, 70, window=self.slider_abn)
        
        button_fit = tk.Button(text='Fit', command=lambda: self.fit(controller))
        self.canvas.create_window(600, 75, window=button_fit)

        label_elmt = tk.Label(controller, text='ELMT:')
        self.canvas.create_window(550, 25, window=label_elmt)
        self.entry_elmt = tk.Entry(controller)
        self.canvas.create_window(650, 25, window=self.entry_elmt)
        self.set_text(self.entry_elmt, self.elmt)

        label_center = tk.Label(controller, text='CENT:')
        self.canvas.create_window(550, 50, window=label_center)
        self.entry_center = tk.Entry(controller)
        self.canvas.create_window(650, 50, window=self.entry_center)
        self.set_text(self.entry_center, self.center)

    def fit(self, controller):
        self.params['vrot'] = self.entry_vrot.get()
        self.params['vmac'] = self.entry_vmac.get()

        model = user_settings.MOD_DIR + controller.current_model
        self.params['abn'] = self.entry_abn.get()
        self.params['elmt'] = self.entry_elmt.get()
        self.params['center'] = self.entry_center.get()
        global global_center
        global_center = float(self.entry_center.get())
        synthe.update_model(self.params, self.entry_abn.get(), model)
        synthe.run_synthe(self.params, model)

        controller.update()

    @staticmethod
    def set_text(entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def current_params(self):
        return f"{self.params['vmac']},{self.params['vrot']},{self.params['resolution']},{self.params['abn']}"

class FitPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.fig = plt.Figure(figsize=(7,6))
        self.canvas = FigureCanvasTkAgg(self.fig, controller)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.ax = self.fig.add_subplot(111)

        self.xlim = (global_center - user_settings.XDELTA, global_center + user_settings.XDELTA)
        self.ylim = (user_settings.YTOP - user_settings.YDELTA, user_settings.YTOP)
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)

        self.fig.subplots_adjust(bottom=0.35)

        ax_deltax = self.fig.add_axes([0.1, 0.1, 0.8, 0.03])
        self.s_deltax = Slider(ax_deltax, r'$\pm$ x', 0.05, 0.5, valinit=user_settings.XDELTA)
        self.s_deltax.on_changed(self.limupdate)

        ax_deltay = self.fig.add_axes([0.1, 0.15, 0.8, 0.03])
        self.s_deltay = Slider(ax_deltay, r'$\pm$ y', 0.01, 1.02, valinit=user_settings.YDELTA)
        self.s_deltay.on_changed(self.limupdate)
        
        dx = 25
        dy = 0.4

        ax_deltasyn_x = self.fig.add_axes([0.1, 0.20, 0.8, 0.03])
        self.s_deltasyn_x = Slider(ax_deltasyn_x, r"$\pm$ Sx", -dx, dx, valinit=0)
        self.s_deltasyn_x.on_changed(self.wiggle)

        ax_deltasyn_y = self.fig.add_axes([0.1, 0.25, 0.8, 0.03])
        self.s_deltasyn_y = Slider(ax_deltasyn_y, r"$\pm$ Sy", -dy, dy, valinit=0)
        self.s_deltasyn_y.on_changed(self.wiggle)

        self.real_x = []
        self.real_y = []

        self.syn_x = []
        self.syn_y = []

        self.real_spec, = self.ax.plot(self.real_x, self.real_y, marker='o', color='k', linestyle='')
        self.syn_spec, = self.ax.plot(self.syn_x, self.syn_y, marker=user_settings.SYN_MARKER, linestyle=user_settings.SYN_LS)

    def synupdate(self):
        if os.path.exists('./synthe/br.dat'):
            syn = pd.read_fwf('./synthe/br.dat', header=None)
            self.syn_x = (syn[0]/10).to_numpy()
            self.syn_y = syn[3].to_numpy()
            self.syn_spec.set_data(self.syn_x, self.syn_y)
            self.wiggle(None)
        self.canvas.draw()
    
    def limupdate(self, _):
        self.xlim = (global_center - self.s_deltax.val, global_center + self.s_deltax.val)
        self.ylim = (user_settings.YTOP - self.s_deltay.val, user_settings.YTOP)
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)

    def wiggle(self, _):
        # self.syn_spec.set_data(self.syn_x + self.s_deltasyn_x.val, self.syn_y + self.s_deltasyn_y.val)
        self.syn_spec.set_data(self.dopler(self.syn_x, self.s_deltasyn_x.val), [y + self.s_deltasyn_y.val for y in self.syn_y])
        
    def dopler(self, xs, v):
        l = []
        for x in xs:
            l.append(-(v / 299792.458) * x + x)
        return l

    # Hardcoded to turn dat file into nm
    def draw_new(self, controller):
        if controller.current_spec[-5:] == '.fits':
            wvl, flx = pyasl.read1dFitsSpec(user_settings.SPEC_DIR + controller.current_spec)
        else:
            df = pd.read_csv(user_settings.SPEC_DIR + controller.current_spec, header=None, sep='\s+')
            wvl = df[0].values / 10
            flx = df[1].values 
        self.real_x = wvl
        self.real_y = flx
        self.real_spec.set_data(self.real_x, self.real_y)
        self.syn_spec.set_data([], [])
        self.canvas.draw()
