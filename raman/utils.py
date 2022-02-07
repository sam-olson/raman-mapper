import datetime

import numpy as np
from scipy import sparse
from scipy.optimize import curve_fit
from scipy.sparse.linalg import spsolve

def timestamp():
	"""
	Creates timestamp in format YYYYMMDD_HHMMSS (i.e. 20220206_113320)
	"""

	return datetime.datetime.now().strftime("%y%m%d_%H%M%S")

def subset(wavenums, intensities, start_wavenum, end_wavenum):
	"""
	Function that creates subset of array based on wavenums

	Parameters
	----------
	wavenums: numpy array holding wavenumbers of complete spectrum
	intensities: numpy array holding intensities of complete spectrum
	start_wavenum: wavenumber at beginning of peak of interest
	end_wavenum: wavenumber at end of peak of interest
	"""

	if start_wavenum < np.min(wavenums):
		start_index = 0
	else:
		start_index = np.argmax(wavenums >= start_wavenum)

	if end_wavenum > np.max(wavenums):
		end_index = len(wavenums) - 1
	else:
		end_index = np.argmax(wavenums >= end_wavenum)

	return wavenums[start_index:end_index], intensities[start_index:end_index]

# borrowed from stackoverflow.com/questions/29156532
# more about asymmetric least squares: https://pubs.rsc.org/en/content/articlehtml/2015/an/c4an01061b
def baseline_als(y, lam=10000, p=0.001, niter=10):
	"""
	Removes baseline from Raman spectrum

	Parameters
	----------
	y: intensity spectrum
	lam: smoothness parameter (lambda)
	p: asymmetry parameter (recommended between 0.001 - 0.1)
	niter: number of iterations to perform

	Returns
	----------
	Input Raman spectrum with baseline removed
	"""

	L = len(y)
	D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L-2))
	w = np.ones(L)

	for i in range(niter):
		W = sparse.spdiags(w, 0, L, L)
		Z = W + lam * D.dot(D.transpose())
		z = spsolve(Z, w*y)
		w = p * (y > z) + (1 - p) * (y < z)
	return z

def lorentzian(x, amp, gamm, x_0):
	"""
	Calculates Lorentzian (Cauchy) Distribution with the given parameters

	Parameters
	----------
	x: numpy array representing x-axis data
	amp: amplitude of distribution
	gamm: gamma (scale parameter)
	x_0: location of peak

	Returns
	----------
	numpy array containin y-axis data of distribution
	"""

	return (amp/(np.pi*gamm)) * ((gamm**2)/(((x-x_0)**2)+(gamm**2)))

def fit_lorentzian(x, y, p0=(2000,2000,1600)):
	"""
	Fits a single lorentzian distribution to a peak (using the lorentzian function)

	Parameters
	----------
	x: x-axis data (wavenumbers)
	y: y-axis data (intensity)
	p0: tuple containing initial guesses for amplitude, full width half maximum, and peak location

	Returns
	----------
	best fit of amplitude, full width half maximum, and peak location
	"""

	try:
		return curve_fit(lorentzian, x, y, p0=p0)[0]
	except RuntimeError:
		# if the max number of iterations is exceeded, a RuntimeError will be created, here this is
		#  just ignored and the point is not filled in on the heatmap
		print("Failed to converge")
		return None

def signal_noise_ratio(wavenums, intensities, start_wavenum, end_wavenum):
	"""
	Calculates the signal to noise ratio of a spectrum

	Parameters
	----------
	wavenums: x-axis data of spectrum
	intensities: y-axis data of spectrum
	start_wavenum: start of wavenumber range on which to calculate signal to noise
	end_wavenum: end of wavenumber range on which to calculate signal to noise

	Returns
	----------
	Signal to noise ratio (max intensity in the range divided by the standard deviation)
	"""

	return np.max(intensities) / np.std(subset(wavenums, 
		intensities, 
		start_wavenum, 
		end_wavenum)[1])

def find_index(x, min_val, delta, max_=None):
	"""
	Finds index of given value in evenly spaced array 

	Parameters
	----------
	x: value of interest
	min_val: lowest value in evenly spaced array
	delta: rate of change of evenly spaced array
	max_: current hacky way to get around higher-than-possible indices (need to fix)
	"""

	index = int((x - min_val) / delta) - 1
	if index < 0:
		index = 0
	if max_:
		if index > max_:
			index = max_
	return index

def summ_stats(arr):
	"""
	Creates summary statistic dictionary of an array

	Parameters
	----------
	arr: array to analyze
	"""

	data = {"mean": round(np.mean(arr), 3),
			"stdev": round(np.std(arr), 3),
			"max": round(np.max(arr), 3),
			"min": round(np.min(arr), 3)}
	return data
