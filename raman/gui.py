import json
import os
import tkinter as tk
from tkinter import filedialog as fd

import pandas as pd
from PIL import Image, ImageTk

import raman.config
from raman.heatmap import HeatMap
import raman.material
from raman.ramanmap import GrapheneRamanMap
from raman.utils import timestamp


def auto_update_entry(entry, value):
	"""
	Programatically inserts given value into tkinter entry box

	Parameters
	----------
	entry: tkinter Entry widget
	value: value to put in Entry widget
	"""

	entry.delete(0, tk.END)
	entry.insert(0, value)

class App(tk.Frame):
	def __init__(self, master=None):
		"""
		Main GUI class, inherits from tk.Frame object
		"""

		super().__init__(master)

		self.master = master
		self.selected_file = ""
		self.current_map = None
		self.material = ""
		self.time_synthesized = ""
		self.growth_method = ""
		self.growth_details = ""

		self.grid(column=0, row=0)
		self._build_frames()
		self._place_file_input_frame()
		self._place_filter_frame()
		self._place_growth_char_frame()
		self._place_analysis_frame()

		self.image_editing_window = False

		self.ratio2dg_heatmap_image = None
		self.ratiodg_heatmap_image = None
		self.locd_heatmap_image = None
		self.locg_heatmap_image = None
		self.loc2d_heatmap_image = None

		self.save_dir = None
	
	def _build_frames(self):
		"""
		Method for building out sub-frames
		"""
		self.file_input_frame = tk.LabelFrame(self)
		self.file_input_frame.grid(column=0, row=0, columnspan=6, rowspan=3, sticky="wens")
		self.file_input_frame.grid_columnconfigure(0, weight=1)

		self.filter_frame = tk.LabelFrame(self)
		self.filter_frame.grid(column=0, row=3, columnspan=6, rowspan=3, sticky="wens")
		self.filter_frame.grid_columnconfigure(0, weight=1)

		self.growth_char_frame = tk.LabelFrame(self)
		self.growth_char_frame.grid(column=0, row=6, columnspan=4, rowspan=3, sticky="wens")
		self.growth_char_frame.grid_columnconfigure(0, weight=1)

		self.analysis_frame = tk.LabelFrame(self)
		self.analysis_frame.grid(column=0, row=11, columnspan=6, rowspan=4, sticky="wens")
		self.analysis_frame.grid_columnconfigure(0, weight=1)

	def _place_file_input_frame(self):
		"""
		Method for placing file input frame
		"""
		self.status_label = tk.Label(self.file_input_frame, text="")
		self.status_label.grid(column=0, row=0, columnspan=6, sticky="wens")
		self.status_label.grid_columnconfigure(0, weight=1)

		# Source file label
		self.source_file_label = tk.Label(self.file_input_frame, 
				text="Load Raman Map File",
				font=("Arial", 18, "bold"))
		self.source_file_label.grid(column=0, row=1, columnspan=6, sticky="ew")

		# Source file name label
		self.source_file_name = tk.Label(self.file_input_frame, text="")
		self.source_file_name.grid(column=0, row=2, columnspan=4, sticky="ew")

		# Source file open button
		self.open_file_button = tk.Button(self.file_input_frame, text="Open", command=self._choose_file)
		self.open_file_button.grid(column=4, row=2, columnspan=2, sticky="ew")

		# Material selection label
		self.mat_selection_label = tk.Label(self.file_input_frame, text="Select Material")
		self.mat_selection_label.grid(column=0, row=3, columnspan=4, sticky="ew")
		
		# Material selection dropdown menu
		self.mat_selection_var = tk.StringVar(self.file_input_frame)
		self.mat_selection_var.set("")

		# TODO: allow for selection of defined materials
		self.mat_selection_menu = tk.OptionMenu(self.file_input_frame, self.mat_selection_var, *["Graphene", "MoS2"])
		self.mat_selection_menu.grid(column=4, row=3, columnspan=2, sticky="ew")
	
	def _place_filter_frame(self):
		"""
		Method for placing filtering frame
		"""

		# Filter section label
		self.filter_sec_label = tk.Label(self.filter_frame, 
				text="Filtering", 
				font=("Arial", 18, "bold"))
		self.filter_sec_label.grid(column=0, row=2, columnspan=6, sticky="ew")

		# Signal to noise ratio label
		self.snr_label = tk.Label(self.filter_frame, text="Input signal to noise ratio")
		self.snr_label.grid(column=0, row=3, columnspan=6, sticky="ew")

		# Signal to noise ratio entry
		self.snr_entry = tk.Entry(self.filter_frame)
		self.snr_entry.insert(0, "15")
		self.snr_entry.grid(column=0, row=4, columnspan=3, sticky="ew")

		# Signal to noise ratio button
		self.snr_button = tk.Button(self.filter_frame, text="Filter", command=self._filter_spectra)
		self.snr_button.grid(column=4, row=4, columnspan=3, sticky="ew")

		# Signal to noise save bad spectra checkbox
		self.snr_checkbox_var = tk.IntVar(self.filter_frame, value=0)
		self.snr_checkbox = tk.Checkbutton(self.filter_frame, variable=self.snr_checkbox_var, text="Save bad spectra?")
		self.snr_checkbox.grid(column=0, row=5, sticky="ew", columnspan=6)
	
	def _place_growth_char_frame(self):
		"""
		Method for placing growth characterstics frame
		"""

		# Growth characteristics section label
		self.growth_char_section_label = tk.Label(self.growth_char_frame,
				text="Growth Characteristics",
				font=("Arial", 18, "bold"))
		self.growth_char_section_label.grid(column=0, row=6, columnspan=6, sticky="ew")

		# Material designation label
		self.mat_desig_label = tk.Label(self.growth_char_frame, text="Material")
		self.mat_desig_label.grid(column=0, row=7, columnspan=3, sticky="ew")

		# Material designation entry
		self.mat_desig_entry = tk.Entry(self.growth_char_frame)
		self.mat_desig_entry.grid(column=0, row=8, columnspan=3, sticky="ew")

		# Date/time synthesized label
		self.time_synth_label = tk.Label(self.growth_char_frame, text="Date/time synthesized")
		self.time_synth_label.grid(column=3, row=7, columnspan=3, sticky="ew")

		# Date/time synthesized entry
		self.time_synth_entry = tk.Entry(self.growth_char_frame)
		self.time_synth_entry.grid(column=3, row=8, columnspan=3, sticky="ew")

		# Growth method label
		self.growth_method_label = tk.Label(self.growth_char_frame, text="Growth method")
		self.growth_method_label.grid(column=0, row=9, columnspan=3, sticky="ew")

		# Growth method entry
		self.growth_method_entry = tk.Entry(self.growth_char_frame)
		self.growth_method_entry.grid(column=0, row=10, columnspan=3, sticky="ew")

		# Growth details label
		self.growth_details_label = tk.Label(self.growth_char_frame, text="Growth details")
		self.growth_details_label.grid(column=3, row=9, columnspan=3, sticky="ew")

		# Growth details text box
		self.growth_details_tb = tk.Text(self.growth_char_frame, height=5, width=52, bg="light yellow")
		self.growth_details_tb.grid(column=3, row=10, columnspan=3, sticky="ew")
	
	def _place_analysis_frame(self):
		"""
		Method for placing data analysis frame
		"""

		# Frame label
		self.data_analysis_label = tk.Label(self.analysis_frame, 
				text="Data Analysis",
				font=("arial", 18, "bold"))
		self.data_analysis_label.grid(column=0, row=11, columnspan=6, sticky="ew")

		# Peak ratio map selection
		self.peak_ratio_map_var = tk.IntVar(self.analysis_frame, value=1)
		self.peak_ratio_map_cb = tk.Checkbutton(self.analysis_frame, 
				variable=self.peak_ratio_map_var, text="Peak ratio maps")
		self.peak_ratio_map_cb.grid(column=0, row=12, columnspan=2, sticky="ew")

		# Peak ratio histogram selection
		self.peak_ratio_hist_var = tk.IntVar(self.analysis_frame, value=1)
		self.peak_ratio_hist_cb = tk.Checkbutton(self.analysis_frame, 
				variable=self.peak_ratio_hist_var, text="Peak ratio histograms")
		self.peak_ratio_hist_cb.grid(column=2, row=12, columnspan=2, sticky="ew")

		# Average spectrum selection
		self.avg_spectrum_var = tk.IntVar(self.analysis_frame, value=1)
		self.avg_spectrum_cb = tk.Checkbutton(self.analysis_frame, 
				variable=self.avg_spectrum_var, text="Average spectrum")
		self.avg_spectrum_cb.grid(column=4, row=12, columnspan=2, sticky="ew")

		# Peak location map selection
		self.peak_loc_map_var = tk.IntVar(self.analysis_frame, value=1)
		self.peak_loc_map_cb = tk.Checkbutton(self.analysis_frame, 
				variable=self.peak_loc_map_var, text="Peak location maps")
		self.peak_loc_map_cb.grid(column=0, row=13, columnspan=2, sticky="ew")

		# Peak location histogram selection
		self.peak_loc_hist_var = tk.IntVar(self.analysis_frame, value=1)
		self.peak_loc_hist_cb = tk.Checkbutton(self.analysis_frame, 
				variable=self.peak_loc_hist_var, text="Peak location histograms")
		self.peak_loc_hist_cb.grid(column=2, row=13, columnspan=2, sticky="ew")

		# Summary statistics selection
		self.summ_stat_var = tk.IntVar(self.analysis_frame, value=1)
		self.summ_stat_cb = tk.Checkbutton(self.analysis_frame, 
				variable=self.summ_stat_var, text="Summary stats")
		self.summ_stat_cb.grid(column=4, row=13, columnspan=2, sticky="ew")

		# Run button
		self.run_button = tk.Button(self.analysis_frame, 
				text="Run", 
				command=self._run_analysis)
		self.run_button.grid(column=0, row=14, columnspan=6, sticky="ew")

	
	def _choose_file(self):
		"""
		File open button handler function, prompts user to select a .csv or .txt file containing
		 map data
		"""

		try:
			self.selected_file = fd.askopenfilename(defaultextension=".csv", 
					filetypes=[("All files", "*.*"), ("CSV files", "*.csv"), ("TXT files", "*.txt")])
			self.source_file_name["text"] = self.selected_file
			self.status_label["text"] = "Loading map..."
			self.current_map = GrapheneRamanMap(self.selected_file, raman.config.GRAPHENE)
			self.status_label["text"] = "Map loaded"
			self.status_label["background"] = "green"
		except FileNotFoundError:
			self.status_label["text"] = "Map not found!"
			self.status_label["background"] = "red"

	def _filter_spectra(self):
		"""
		Filter spectra button handler function, filters low signal-to-noise ratio spectra in the map,
		 saves bad spectra if requested
		"""
		if self.current_map:
			self.status_label["text"] = "Filtering data..."
			self.status_label["background"] = None
			if self.snr_checkbox_var.get():
				save_path = os.path.join(os.path.dirname(self.selected_file),
						f"{os.path.basename(self.selected_file).split('.')[0]}_bad_spectra")
				os.mkdir(save_path)
			else:
				save_path = None
			self.current_map.data_summary(int(self.snr_entry.get()), save_path)
			self.status_label["text"] = "Data filtered"
			self.status_label["background"] = "green"

		else:
			self.status_label["text"] = "Please select a map before filtering"
			self.status_label["background"] = "red"
		
	def _run_analysis(self):
		"""
		Run analysis button handler function, runs selected analysis methods
		"""

		if self.current_map:
			self.save_dir = os.path.join(os.path.dirname(self.selected_file),
					f"{os.path.basename(self.selected_file).split('.')[0]}")

			# creating a directory to store results
			if os.path.exists(self.save_dir):
				self.save_dir = f"{self.save_dir}_{timestamp()}"

			os.mkdir(self.save_dir)
			
			# string containing growth characteristics data
			growth_char_string = (f"MATERIAL\n----------\n{self.mat_desig_entry.get()}\n\n"
					f"DATE/TIME SYNTHESIZED\n----------\n{self.time_synth_entry.get()}\n\n"
					f"GROWTH METHOD\n----------\n{self.growth_method_entry.get()}\n\n"
					f"GROWTH DETAILS\n----------\n{self.growth_details_tb.get('1.0', 'end-1c')}")

			# ...saving growth characteristics
			with open(os.path.join(self.save_dir, "growth_characteristics.txt"), "w") as f:
				f.write(growth_char_string)

			# creating heatmaps of peak ratios if requested
			if self.peak_ratio_map_var.get():
				self.image_editing_window = True
				self.ratio2dg_heatmap_image = self.current_map.create_heatmap("ratio_2dg", None, None)
				self.ratiodg_heatmap_image = self.current_map.create_heatmap("ratio_dg", None, None)

			# creating histograms of peak ratios if requested
			if self.peak_ratio_hist_var.get():
				self.current_map.create_histogram("ratio_2dg", 
						"2D:G Ratio",
						os.path.join(self.save_dir, "ratio_2dg_hist.png"))
				self.current_map.create_histogram("ratio_dg",
						"D:G Ratio",
						os.path.join(self.save_dir, "ratio_dg_hist.png"))

			# creating average spectrum if requested
			if self.avg_spectrum_var.get():
				self.current_map.average_spectrum(os.path.join(self.save_dir, "average_spectrum.png"))

			# creating peak location heatmap if requested
			if self.peak_loc_map_var.get():
				self.image_editing_window = True
				self.locd_heatmap_image = self.current_map.create_heatmap("peak_loc_d", None, None)
				self.locg_heatmap_image = self.current_map.create_heatmap("peak_loc_g", None, None)
				self.loc2d_heatmap_image = self.current_map.create_heatmap("peak_loc_2d", None, None)

			# creating peak location histogram if requested
			if self.peak_loc_hist_var.get():
				self.current_map.create_histogram("peak_loc_d",
						"D Peak Location (cm^-1)",
						os.path.join(self.save_dir, "peak_loc_d_hist.png"))
				self.current_map.create_histogram("peak_loc_g",
						"G Peak Location (cm^-1)",
						os.path.join(self.save_dir, "peak_loc_g_hist.png"))
				self.current_map.create_histogram("peak_loc_2d",
						"2D Peak Location (cm^-1)",
						os.path.join(self.save_dir, "peak_loc_2d_hist.png"))

			# creating summary statistics file if requested
			if self.summ_stat_var.get():
				self.current_map.category_statistics(os.path.join(self.save_dir, "statistics.csv"))

			# if any heatmaps were requested...
			if self.image_editing_window:	
				# ...create the image editing window
				self._image_editor()
				
				self.img_save_button = tk.Button(self, text="Save Images", command=self._save_imgs)
				self.img_save_button.grid(column=0, row=20, columnspan=6)
				self.img_save_button.grid_columnconfigure(0, weight=1)

	def _image_editor(self):
		"""
		Method for creating the image editing window, this allows users to modify heatmaps
		 before saving them (users can also save/load previous templates)
		"""

		# creating peak ratio heatmap editor frames if requested
		if self.ratio2dg_heatmap_image:
			self.ratio2dg_ie = ImageEditor(self, HeatMap(self.current_map, "ratio_2dg", "2D:G Ratio"))
			self.ratio2dg_ie.grid(column=0, row=15, columnspan=6)
			self.ratio2dg_ie.grid_columnconfigure(0, weight=1)

			self.ratiodg_ie = ImageEditor(self, HeatMap(self.current_map, "ratio_dg", "D:G Ratio"))
			self.ratiodg_ie.grid(column=0, row=16, columnspan=6)
			self.ratiodg_ie.grid_columnconfigure(0, weight=1)

		# creating peak location heatmap editor frames if requested
		if self.locd_heatmap_image:
			self.locd_ie = ImageEditor(self, HeatMap(self.current_map, "peak_loc_d", "D Peak Location"))
			self.locd_ie.grid(column=0, row=17, columnspan=6)
			self.locd_ie.grid_columnconfigure(0, weight=1)

			self.locg_ie = ImageEditor(self, HeatMap(self.current_map, "peak_loc_g", "G Peak Location"))
			self.locg_ie.grid(column=0, row=18, columnspan=6)
			self.locg_ie.grid_columnconfigure(0, weight=1)

			self.loc2d_ie = ImageEditor(self, HeatMap(self.current_map, "peak_loc_2d", "2D Peak Location"))
			self.loc2d_ie.grid(column=0, row=19, columnspan=6)
			self.loc2d_ie.grid_columnconfigure(0, weight=1)

	def _save_imgs(self):
		"""
		Save image button handler function

		- Save heatmap
		- Save scalebar
		- Save scalebar range information
		"""

		# dictionary for storing scalebar range information
		scale_range = {"statistic": [],
				"scale_bot": [],
				"scale_top": [],
				"x-range": [],
				"y-range": []}

		# save peak ratio heatmaps if present
		if self.ratio2dg_heatmap_image:
			self.ratio2dg_ie.save_image()
			scale_range["statistic"].append("2D:G Ratio")
			scale_range["scale_bot"].append(self.ratio2dg_ie.heatmap.scale_bot)
			scale_range["scale_top"].append(self.ratio2dg_ie.heatmap.scale_top)
			rmap = self.ratio2dg_ie.heatmap.rmap
			scale_range["x-range"].append(f"{rmap.min_x - rmap.min_x} - {rmap.max_x - rmap.min_x}")
			scale_range["y-range"].append(f"{rmap.min_y - rmap.min_y} - {rmap.max_y - rmap.min_y}")

			self.ratiodg_ie.save_image()
			scale_range["statistic"].append("D:G Ratio")
			scale_range["scale_bot"].append(self.ratiodg_ie.heatmap.scale_bot)
			scale_range["scale_top"].append(self.ratiodg_ie.heatmap.scale_top)
			rmap = self.ratiodg_ie.heatmap.rmap
			scale_range["x-range"].append(f"{rmap.min_x - rmap.min_x} - {rmap.max_x - rmap.min_x}")
			scale_range["y-range"].append(f"{rmap.min_y - rmap.min_y} - {rmap.max_y - rmap.min_y}")

		# save peak location heatmaps if present
		if self.locd_heatmap_image:
			self.locd_ie.save_image()
			scale_range["statistic"].append("D Peak Location")
			scale_range["scale_bot"].append(self.locd_ie.heatmap.scale_bot)
			scale_range["scale_top"].append(self.locd_ie.heatmap.scale_top)
			rmap = self.locd_ie.heatmap.rmap
			scale_range["x-range"].append(f"{rmap.min_x - rmap.min_x} - {rmap.max_x - rmap.min_x}")
			scale_range["y-range"].append(f"{rmap.min_y - rmap.min_y} - {rmap.max_y - rmap.min_y}")

			self.locg_ie.save_image()
			scale_range["statistic"].append("G Peak Location")
			scale_range["scale_bot"].append(self.locg_ie.heatmap.scale_bot)
			scale_range["scale_top"].append(self.locg_ie.heatmap.scale_top)
			rmap = self.locg_ie.heatmap.rmap
			scale_range["x-range"].append(f"{rmap.min_x - rmap.min_x} - {rmap.max_x - rmap.min_x}")
			scale_range["y-range"].append(f"{rmap.min_y - rmap.min_y} - {rmap.max_y - rmap.min_y}")

			self.loc2d_ie.save_image()
			scale_range["statistic"].append("2D Peak Location")
			scale_range["scale_bot"].append(self.loc2d_ie.heatmap.scale_bot)
			scale_range["scale_top"].append(self.loc2d_ie.heatmap.scale_top)
			rmap = self.loc2d_ie.heatmap.rmap
			scale_range["x-range"].append(f"{rmap.min_x - rmap.min_x} - {rmap.max_x - rmap.min_x}")
			scale_range["y-range"].append(f"{rmap.min_y - rmap.min_y} - {rmap.max_y - rmap.min_y}")

		# save scalebar range information to .csv
		if len(scale_range["statistic"]) > 0:
			pd.DataFrame(data=scale_range).to_csv(os.path.join(self.save_dir, "scalebar_ranges.csv"), index=False)


class ImageEditor(tk.LabelFrame):
	def __init__(self, master, heatmap):
		"""
		Window that allows user to modify heatmap images in real time before saving them

		Users can change...
		- Numerical start/stop range of scalebar
		- Scalebar color range
		- Scalebar gradient (i.e. how many colors between min/max)
		- Scaling interpolation method
		- Final image save size

		Parameters
		----------
		master: typically the parent frame 
		heatmap: current heatmap being analyzed
		"""

		super().__init__(master)

		self.master = master
		self.heatmap = heatmap

		# getting default values from heatmap...
		self.min_val = round(self.heatmap.scale_bot, 3)
		self.max_val = round(self.heatmap.scale_top, 3)
		self.gradient = self.heatmap.gradient
		self.interp_method = self.heatmap.resize_method
		self.start_col = self.heatmap.start_color
		self.end_col = self.heatmap.end_color
		self.final_width = 200

		# dictionary that hashes relation between PIL constants and strings
		self.interp_val_decode = {"NEAREST": Image.NEAREST,
				"BILINEAR": Image.BILINEAR,
				"BICUBIC": Image.BICUBIC,
				"LANCZOS": Image.LANCZOS}

		# Title
		self.title_label = tk.Label(self, text=f"{self.heatmap.title} heatmap", font=("arial", 16, "bold"))
		self.title_label.grid(column=0, row=0, columnspan=6)

		# Creating and placing the image
		self.img_tk = ImageTk.PhotoImage(self.heatmap.img.resize((200,200)))
		self.img_label = tk.Label(self, image=self.img_tk)
		self.img_label.image = self.img_tk
		self.img_label.grid(column=0, row=1)

		# Scalebar
		self.sb_tk = ImageTk.PhotoImage(self.heatmap.scalebar.resize((20, 100), Image.NEAREST))
		self.sb_label = tk.Label(self, image=self.sb_tk)
		self.sb_label.image = self.sb_tk
		self.sb_label.grid(column=1, row=1)

		# Minimum value label and entry
		self.min_val_label = tk.Label(self, text="Minimum value")
		self.min_val_label.grid(column=0, row=2, columnspan=3, sticky="ew")
		self.min_val_entry = tk.Entry(self)
		self.min_val_entry.insert(tk.END, self.min_val)
		self.min_val_entry.grid(column=0, row=3, columnspan=3, sticky="ew")

		# Maximum value label and entry
		self.max_val_label = tk.Label(self, text="Maximum value")
		self.max_val_label.grid(column=0, row=4, columnspan=3, sticky="ew")
		self.max_val_entry = tk.Entry(self)
		self.max_val_entry.insert(tk.END, self.max_val)
		self.max_val_entry.grid(column=0, row=5, columnspan=3, sticky="ew")

		# Gradient label and entry
		self.gradient_label = tk.Label(self, text="Gradient")
		self.gradient_label.grid(column=0, row=6, columnspan=3, sticky="ew")
		self.gradient_entry = tk.Entry(self)
		self.gradient_entry.insert(tk.END, self.gradient)
		self.gradient_entry.grid(column=0, row=7, columnspan=3, sticky="ew")

		# Interpolation method menu
		self.interp_method_label = tk.Label(self, text="Interpolation method")
		self.interp_method_label.grid(column=0, row=8, columnspan=3, sticky="ew")
		self.interp_method_var = tk.StringVar(self)
		self.interp_method_var.set("BICUBIC")
		self.interp_method_menu = tk.OptionMenu(self, 
				self.interp_method_var, 
				*["NEAREST", "BILINEAR", "BICUBIC", "LANCZOS"])
		self.interp_method_menu.grid(column=0, row=9, columnspan=3, sticky="ew")

		# Start color label and entry
		self.start_col_label = tk.Label(self, text="Color scale start")
		self.start_col_label.grid(column=3, row=2, columnspan=3, sticky="ew")
		self.start_col_entry = tk.Entry(self)
		self.start_col_entry.insert(tk.END, self.start_col)
		self.start_col_entry.grid(column=3, row=3, columnspan=3, sticky="ew")

		# End color label and entry
		self.end_col_label = tk.Label(self, text="Color scale end")
		self.end_col_label.grid(column=3, row=4, columnspan=3, sticky="ew")
		self.end_col_entry = tk.Entry(self)
		self.end_col_entry.insert(tk.END, self.end_col)
		self.end_col_entry.grid(column=3, row=5, columnspan=3, sticky="ew")

		# Final picture width label and entry
		self.pic_width_label = tk.Label(self, text="Final picture width (pix)")
		self.pic_width_label.grid(column=3, row=6, columnspan=3, sticky="ew")
		self.pic_width_entry = tk.Entry(self)
		self.pic_width_entry.insert(tk.END, self.final_width)
		self.pic_width_entry.grid(column=3, row=7, columnspan=3, sticky="ew")

		# Update button
		self.update_button = tk.Button(self, text="Update", command=self._update)
		self.update_button.grid(column=3, row=8, columnspan=1, rowspan=2, sticky="news")

		# Save template button
		self.save_templ_button = tk.Button(self, text="Save Templ.", command=self._save_templ)
		self.save_templ_button.grid(column=4, row=8, columnspan=2, rowspan=1, sticky="news")

		# Load template button
		self.load_templ_button = tk.Button(self, text="Load Templ.", command=self._load_templ)
		self.load_templ_button.grid(column=4, row=9, columnspan=2, rowspan=1, sticky="news")

	
	def _update(self):
		"""
		Update button handler function, takes user input and applies it to heatmap
		"""

		self.heatmap.scale_bot = float(self.min_val_entry.get())
		self.heatmap.scale_top = float(self.max_val_entry.get())
		self.heatmap.gradient = int(self.gradient_entry.get())
		self.heatmap.resize_method = self.interp_val_decode.get(self.interp_method_var.get())
		self.heatmap.start_color = self.start_col_entry.get()
		self.heatmap.end_color = self.end_col_entry.get()
		self.heatmap.save_width = int(self.pic_width_entry.get())
		self.heatmap.calc_img()

		
		self.img_tk = ImageTk.PhotoImage(self.heatmap.img.resize((200,200), 
				self.interp_val_decode.get(self.interp_method_var.get())))
		self.img_label = tk.Label(self, image=self.img_tk)
		self.img_label.image = self.img_tk
		self.img_label.grid(column=0, row=1)

		self.sb_tk = ImageTk.PhotoImage(self.heatmap.scalebar.resize((20, 100), Image.NEAREST))
		self.sb_label = tk.Label(self, image=self.sb_tk)
		self.sb_label.image = self.sb_tk
		self.sb_label.grid(column=1, row=1)

	def _save_templ(self):
		"""
		Save heatmap template button handler function, saves current heatmap settings in a .json file
		"""

		# update heatmap prior to saving
		self._update()

		data = {"statistic": self.heatmap.statistic,
				"min_val": float(self.min_val_entry.get()),
				"max_val": float(self.max_val_entry.get()),
				"gradient": int(self.gradient_entry.get()),
				"resize_method": self.interp_val_decode.get(self.interp_method_var.get()),
				"start_col": self.start_col_entry.get(),
				"end_col": self.end_col_entry.get(),
				"save_width": int(self.pic_width_entry.get())}

		with fd.asksaveasfile(mode="w", defaultextension=".json") as f:
			if f is None:
				return
			json.dump(data, f, indent=4)

	def _load_templ(self):
		"""
		Load heatmap template button handler function, lets a user load a previously saved .json template file
		"""

		load_file = fd.askopenfilename(defaultextension=".json", 
				filetypes=[("All files", "*.*"), ("JSON files", "*.json")])

		with open(load_file, "r") as f:
			data = json.load(f)

		auto_update_entry(self.min_val_entry, data["min_val"])
		auto_update_entry(self.max_val_entry, data["max_val"])
		auto_update_entry(self.gradient_entry, data["gradient"])
		auto_update_entry(self.start_col_entry, data["start_col"])
		auto_update_entry(self.end_col_entry, data["end_col"])
		auto_update_entry(self.pic_width_entry, data["save_width"])

		self._update()
	
	def save_image(self):
		"""
		Save images button handler, saves heatmap and scalebar images
		"""

		# width and height for resizing
		w = int(self.pic_width_entry.get())
		h = int(w * self.heatmap.rmap.aspect_ratio)

		sb_thickness = int(h / self.heatmap.scalebar_thickness_ratio)
		method = self.interp_val_decode.get(self.interp_method_var.get())
		self.heatmap.img.resize((w,h), method).save(os.path.join(self.master.save_dir, 
			f"{self.heatmap.statistic}.png"))
		self.heatmap.scalebar.resize((sb_thickness, h)).save(os.path.join(self.master.save_dir, 
			f"{self.heatmap.statistic}_scalebar.png"))

