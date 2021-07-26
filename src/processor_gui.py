import tkinter as tk
import tkinter.filedialog

from processor import ProcessorConfig, processor


class DataElement:
    def __init__(self, initial_value):
        self._value = initial_value
        self.hooks = []

    def add_hook(self, f):
        """Add a function that will be executed when value is changed
        the hooks are the form (old_value, new_value)
        """
        self.hooks.append(f)

    def remove_hook(self, f):
        """Remove the given function"""
        self.hooks.remove(f)

    def update(self, value):
        old_value = self._value
        self._value = value
        for hook in self.hooks:
            hook(old_value, value)

    @property
    def value(self):
        return self._value


class DataHandler:
    def __init__(self):
        self.library = DataElement(None)
        self.mgf = DataElement(None)
        self.output = DataElement(None)
        self.state = DataElement(None)
        self.config = ProcessorConfig()
        self.log = DataElement("")
        self.library.add_hook(lambda _, value: self.set_library(value))
        self.mgf.add_hook(lambda _, value: self.set_mgf(value))
        self.output.add_hook(lambda _, value: self.set_output(value))
        self.parent_mz_tolerance_value = tk.DoubleVar()
        self.msms_mz_tolerance_value = tk.DoubleVar()
        self.min_cosine_score_value = tk.DoubleVar()
        self.min_peaks_value = tk.DoubleVar()
        self.parent_mz_tolerance_value.set(self.config.parent_mz_tolerance)
        self.msms_mz_tolerance_value.set(self.config.msms_mz_tolerance)
        self.min_cosine_score_value.set(self.config.min_cosine_score)
        self.min_peaks_value.set(self.config.min_peaks)

    def log_function(self, data):
        print(data)
        self.log.update(data + "\n")

    def set_library(self, db_file):
        self.config.db_files = [db_file]

    def set_mgf(self, mgf):
        self.config.query_file = mgf

    def set_output(self, output):
        self.config.output_file = output

    def update_config(self):
        self.config.parent_mz_tolerance = self.parent_mz_tolerance_value.get()
        self.config.msms_mz_tolerance = self.msms_mz_tolerance_value.get()
        self.config.min_cosine_score = self.min_cosine_score_value.get()
        self.config.min_peaks = self.min_peaks_value.get()
        print(self.config.min_peaks)


def choose_library():
    name = tkinter.filedialog.askopenfilename()
    dh.library.update(name)


def choose_mgf():
    name = tkinter.filedialog.askopenfilename()
    dh.mgf.update(name)


def choose_output():
    name = tkinter.filedialog.asksaveasfilename()
    dh.output.update(name)


def process():
    if (dh.library.value is None) | (dh.mgf.value is None) | (dh.output.value is None):
        dh.state.update("Please make sure that Library, MGF and Output are set!")
        return
    dh.update_config()  # We update the config with the values in the window
    dh.state.update("Processing, this can take a while...")
    processor(dh.log_function, dh.config)
    dh.state.update("Processed")


root = tk.Tk()
root.geometry('1024x768')

### That's the UI itself

tk.Label(root, text="MS parent ion tolerance").grid(row=0)
tk.Label(root, text="MS/MS ion tolerance").grid(row=1)
tk.Label(root, text="Minimal cosine score").grid(row=2)
tk.Label(root, text="Minimal number of peaks matching").grid(row=3)

dh = DataHandler()

parent_mz_tolerance_entry = tk.Entry(root, textvariable=dh.parent_mz_tolerance_value)
parent_mz_tolerance_entry.grid(row=0, column=1)

msms_mz_tolerance_entry = tk.Entry(root, textvariable=dh.msms_mz_tolerance_value)
msms_mz_tolerance_entry.grid(row=1, column=1)

min_cosine_score_entry = tk.Entry(root, textvariable=dh.min_cosine_score_value)
min_cosine_score_entry.grid(row=2, column=1)

min_peaks_entry = tk.Entry(root, textvariable=dh.min_peaks_value)
min_peaks_entry.grid(row=3, column=1)

label_lib = tk.Label(root, text='No library selected!', fg='green', font=('helvetica', 12, 'bold'))
label_lib.grid(row=4, column=0)
dh.library.add_hook(lambda _, value: label_lib.config(text=value))

button_lib = tk.Button(text='Choose a library', command=choose_library, bg='brown', fg='white')
button_lib.grid(row=4, column=1)

label_mgf = tk.Label(root, text='No MGF selected!', fg='green', font=('helvetica', 12, 'bold'))
label_mgf.grid(row=5, column=0)
dh.mgf.add_hook(lambda _, value: label_mgf.config(text=value))

button_mgf = tk.Button(text='Choose a MGF file', command=choose_mgf, bg='orange', fg='white')
button_mgf.grid(row=5, column=1)

label_output = tk.Label(root, text='No Output selected!', fg='green', font=('helvetica', 12, 'bold'))
label_output.grid(row=6, column=0)
dh.output.add_hook(lambda _, value: label_output.config(text=value))

button_output = tk.Button(text='Choose an output file', command=choose_output, bg='yellow', fg='black')
button_output.grid(row=6, column=1)

button_output = tk.Button(text='Process', command=process, bg='green', fg='white')
button_output.grid(row=7, column=0)

label_status = tk.Label(root, text='', fg='green', font=('helvetica', 12, 'bold'))
label_status.grid(row=7, column=1)
dh.state.add_hook(lambda _, value: label_status.config(text=value))

logbox = tk.Text()
logbox.config(state='disabled')
dh.log.add_hook(lambda _, value: (
    logbox.config(state='normal'),
    logbox.insert("end", value),
    logbox.config(state='disabled')
))
logbox.grid(row=8, columnspan=2)

root.mainloop()
