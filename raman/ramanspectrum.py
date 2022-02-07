import os

import matplotlib.pyplot as plt
import numpy as np

from raman.utils import baseline_als, fit_lorentzian, signal_noise_ratio, subset


class RamanSpectrum:
	"""
	Class for holding information about Raman spectrum

	Parameters
	----------
	wavenums: wavenumbers of Raman spectrum
	intensities: intensities of Raman spectrum
	material: material to which the spectrum belongs
	"""

	def __init__(self, wavenums, intensities, material):
		self.wavenums = wavenums
		self.intensities = intensities

		# subtracting baseline
		self.intensities = self.intensities - baseline_als(self.intensities)

		self.material = material
		self.material_name = material.name
		self.peaks = material.peaks
		self.snr_sample_region = material.snr_sample_region

		# calculating signal-to-noise ratio of spectrum
		self.snr = signal_noise_ratio(self.wavenums,
				self.intensities,
				*self.snr_sample_region)
		
		# dictionary for holding information about ranges of the spectrum containing peaks
		self.peak_subsets = {}

		for k,v  in self.peaks.items():
			self.peak_subsets[k] = subset(self.wavenums, 
					self.intensities, 
					v[0], 
					v[1])
	
	def __len__(self):
		"""
		The length of a RamanSpectrum object is determined by the number of wavenumber samples it has
		"""

		return len(self.wavenums)

	@classmethod
	def from_file(cls, filepath, material):
		"""
		Class method for creating a RamanSpectrum from a .txt file
		"""

		wavenums, intensities = map(np.array, zip(*np.loadtxt(filepath)))
		return cls(wavenums, intensities, material)
	
	def plot_spec(self, **kwargs):
		"""
		Method for plotting the spectrum using matplotlib

		Parameters
		----------
		kwargs: keyword arguments to be used in the matplotlib pyplot.plot function

		Returns
		----------
		matplotlib plot object
		"""

		return plt.plot(self.wavenums, self.intensities, **kwargs)

	def plot_bline(self, lam=10000, p=0.001, niter=10):
		"""
		Method for plotting the baseline of the spectrum

		Parameters
		----------
		lam: lambda value (smoothness parameter)
		p: asymmetry parameter
		niter: number of iterations to perform
		"""

		bline = baseline_als(self.intensities, lam, p, niter)
		plt.subplot(121)
		plt.plot(self.wavenums, self.intensities)
		plt.plot(self.wavenums, bline)
		plt.subplot(122)
		plt.plot(self.wavenums, self.intensities-bline)
		plt.show()
	
