import os
import random

from colour import Color
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from raman.config import GRAPHENE
from raman.ramanspectrum import RamanSpectrum
from raman.utils import find_index, fit_lorentzian, lorentzian, summ_stats

class RamanMap:
	def __init__(self, fpath, material):
		"""
		Main map class from which other map classes inherit

		Parameters
		----------
		fpath: file path to map data
		material: Material class containing information about your material
		"""

		self.fpath = fpath
		self.material = material

		# allowing for loading either .csv or .txt files
		if self.fpath.endswith(".csv"):
			self.df = pd.read_csv(fpath, header=None)
		elif self.fpath.endswith(".txt"):
			self.df = pd.read_csv(fpath, header=None, sep="\t")

		self.x = np.array(self.df.iloc[1:, 0])
		self.y = np.array(self.df.iloc[1:, 1])

		self.min_x = np.min(self.x)
		self.max_x = np.max(self.x)
		self.min_y = np.min(self.y)
		self.max_y = np.max(self.y)

		self.width = self.max_x - self.min_x
		self.height = self.max_y - self.min_y
		self.aspect_ratio = self.height / self.width
		self.unique_x = len(set(self.x))
		self.unique_y = len(set(self.y))

		self.x_step = self.width / (self.unique_x-1)
		self.y_step = self.height / (self.unique_y-1)

		self.data = self.df.iloc[:, 2:].transpose()
		self.wavenums = self.data.iloc[:, 0]
		self.intensities = self.data.iloc[:, 1:]

		# creating a RamanSpectrum object for each spectrum in map
		self.spectra = [RamanSpectrum(self.wavenums, 
			self.intensities.iloc[:, i], 
			self.material) for i in range(len(self.intensities.columns))]
		
		self.spectra_characteristics = [{"present": True,
			"x": self.x[i],
			"y": self.y[i]} for i in range(len(self.spectra))]
	
	def __len__(self):
		return len(self.spectra)

	def remove_noisy(self, thresh=15, savebad=None):
		"""
		removes raman spectra that have a signal-to-noise ratio below the threshold

		parameters
		----------
		thresh: signal-to-noise threshold below which to exclude (default 15)
		savebad: provides ability to save rejected spectra to assure the 
		  threshold is set correctly (should be a path to a directory where you want to save the images)
		"""

		for i, s in enumerate(self.spectra):
			if s.snr < thresh:
				self.spectra_characteristics[i]["present"] = False
				if savebad:
					s.plot_spec()
					plt.savefig(os.path.join(savebad, f"{i}_{int(s.snr)}.png"), dpi=300)
					plt.close()
	
	def create_heatmap(self, 
			statistic,
			savepath, 
			size, 
			start_color = "black", 
			end_color="blue", 
			gradient=10, 
			scale="auto"):
		"""
		Creates a pixel heatmap for a given statistic

		Parameters
		----------
		statistic: the statistic to make a heatmap of
		savepath: filepath to save map image to
		size: width (in pixels) at which to save the image (aspect ratio is retained, height calculated 
		  automatically)
		start_color: for color scale, color that corresponds to lowest values (default black)
		end_color: for color scale, color that corresponds to highest values (default blue)
		gradient: number of steps between high and low colors on scale (default 10)
		scale: if specified, hard limits of color bar scale (tuple if specified, otherwise autocalculated)
		"""
		xs = [d["x"] for d in self.spectra_characteristics]
		ys = [d["y"] for d in self.spectra_characteristics]
		incl = [d["present"] for d in self.spectra_characteristics]
		scale_x = [int(round((i-self.min_x) / self.x_step, 0)) for i in xs]
		scale_y = [int(round((i-self.min_y) / self.y_step, 0)) for i in ys]
		ds = [d[statistic] for d in self.spectra_characteristics]

		if scale == "auto":
			scale_bot = np.min(ds)
			scale_top = np.max(ds)
		elif isinstance(scale, tuple):
			scale_bot = scale[0]
			scale_top = scale[1]
		else:
			raise ValueError("Invalid type, 'scale' must be tuple")

		stat_delta = (scale_top - scale_bot) / gradient
		col_array = list(Color(start_color).range_to(Color(end_color), gradient))

		image_array = np.zeros([self.unique_y, self.unique_x], dtype=(float, 3))

		for x,y,d in zip(scale_x, scale_y, ds):
			pix_color = col_array[find_index(d, scale_bot, stat_delta)].get_rgb()
			pix_color_int = list(map(lambda x: int(x * 255), pix_color))
			image_array[self.unique_y - y - 1][x] = pix_color_int

		img = Image.fromarray(np.uint8(image_array), "RGB")

		if size:
			img = img.resize((size, int(size * self.aspect_ratio)), Image.NEAREST)
		if savepath:
			img.save(savepath)

		return img

	def create_histogram(self, statistic, unit, savepath, **kwargs):
		"""
		Creates a histogram for a given statistic

		Parameters
		----------
		statistic: the statistic to make a histogram of 
		unit: unit of measurement of data
		savepath: where to save the resulting plot to
		kwargs: keyword arguments that will be used in the histogram
		"""
		vals = [d[statistic] for d in self.spectra_characteristics if d["present"]]
		plt.hist(vals, **kwargs)
		plt.xlabel(unit)
		plt.ylabel("Count")
		plt.savefig(savepath)
		plt.close()

	def average_spectrum(self, savepath):
		"""
		Creates average Raman spectrum across map (only spectra that pass SNR test)

		Parameters
		----------
		savepath: path to save image
		"""

		avg_spectrum = np.array([0 for i in self.spectra[0].intensities])
		
		for n, s in enumerate(self.spectra_characteristics):
			if s["present"]:
				spectrum = self.spectra[n]
				for i, j in enumerate(spectrum.intensities):
					avg_spectrum[i] += j

		avg_spectrum = avg_spectrum / len(self.spectra[0])
		plt.plot(self.spectra[0].wavenums, avg_spectrum)
		plt.xlabel("Wavenumber (cm^-1)")
		plt.ylabel("Intensity (a.u.)")
		plt.savefig(savepath)
		plt.close()
					



class GrapheneRamanMap(RamanMap):
	def __init__(self, fpath, material):
		"""
		RamanMap specifically catering to Graphene, inherits from RamanMap class
		"""

		super().__init__(fpath, GRAPHENE)

		self.spectra_characteristics = [{"present": True,
			"x": self.x[i],
			"y": self.y[i],
			"peak_loc_d": 0,
			"peak_loc_g": 0,
			"peak_loc_2d": 0,
			"fwhm_2d": 0,
			"ratio_2dg": 0,
			"ratio_dg": 0} for i in range(len(self.spectra))]
	
	def data_summary(self, thresh=15, savebad=None):
		"""
		removes raman spectra that have a signal-to-noise ratio below the threshold, calculates
		  graphene-specific statistics

		Parameters
		----------
		thresh: signal-to-noise threshold below which to exclude (default 15)
		savebad: provides ability to save rejected spectra to assure the 
		  threshold is set correctly (should be a path to a directory where you want to save the images)
		"""

		self.remove_noisy(thresh, savebad)
		self.g_fits = []
		
		for n, s in enumerate(self.spectra_characteristics):
			if s["present"]:
				spectrum = self.spectra[n]
				params_d = fit_lorentzian(*spectrum.peak_subsets["D"])
				params_g = fit_lorentzian(*spectrum.peak_subsets["G"])
				params_2d = fit_lorentzian(*spectrum.peak_subsets["2D"])

				if any(i is None for i in [params_d, params_g, params_2d]):
					s["present"] = False
				else:
					lor_d = lorentzian(spectrum.peak_subsets["D"], *params_d)
					lor_g = lorentzian(spectrum.peak_subsets["G"], *params_g)
					lor_2d = lorentzian(spectrum.peak_subsets["2D"], *params_2d)
					self.g_fits.append(params_g)

					s["peak_loc_d"] = params_d[2]
					s["peak_loc_g"] = params_g[2]
					s["peak_loc_2d"] = params_2d[2]
					s["fwhm_2d"] = 2 * params_2d[1]
					s["ratio_2dg"] = np.max(lor_2d) / np.max(lor_g)
					s["ratio_dg"] = np.max(lor_d) / np.max(lor_g)
	
	def category_statistics(self, savepath):
		"""
		Calculates summary statistics for each graphene parameter of interest
		"""

		categories = ["peak_loc_d",
				"peak_loc_g",
				"peak_loc_2d",
				"fwhm_2d",
				"ratio_2dg",
				"ratio_dg"]

		data = {"Measurement": [],
				"Mean": [],
				"STDev": [],
				"Max": [],
				"Min": []}

		for i in categories:
			d = summ_stats([j[i] for j in self.spectra_characteristics if j["present"]])
			data["Measurement"].append(i)
			data["Mean"].append(d["mean"])
			data["STDev"].append(d["stdev"])
			data["Max"].append(d["max"])
			data["Min"].append(d["min"])

		pd.DataFrame(data=data).to_csv(savepath, index=False)





