# raman-mapper
A Python GUI for analyzing and characterizing [Raman spectroscopy](https://en.wikipedia.org/wiki/Raman_spectroscopy) maps. Support is currently mostly for graphene or other graphitic materials, further materials may be added depending on interests.

Features of `raman-mapper` include:
- Simple and intuitive UI 
- Ability to filter spectra by signal-to-noise ratio thresholds
- Recording of material properties and synthesis characteristics
- Creating/modifying heatmaps of spectra statistics
- Creating histograms and summary statistics of map information

The base UI:

![raman gui](https://github.com/sam-olson/raman-mapper/blob/main/img/gui_overview.png | width=500)

The aim of this software is to allow end users greater control and customization over their Raman maps, along with greater accuracy made possible by fitting Lorentzian distributions and removing noisy signals. It also allows for saving of heatmap templates, something that is very useful for comparing disparate growths for publications.

## Raman Spectroscopy
### Basics
Raman spectroscopy is a non-destructive analytical technique used to determine properties of materials. At its core, Raman spectroscopy is concerned with the way that light interacts inelastically with bonds in a material. The basic steps include:
1. Shining a laser onto the surface of the material
2. The laser light is shifted up or down in energy by bonds in the material
3. The shifted laser light is collected and dispersed into separate "buckets" collected via a CCD array
4. Intensities for each bucket are recorded and displayed as Intensity vs. Wavenumber (or Raman shift)

Peaks in intensity typically correspond to known bond energies in materials. e [Lorentzian (Cauchy) distributions](https://en.wikipedia.org/wiki/Cauchy_distribution) can be fit to these peaks, with parameters of the distribution giving information about the material properties.

In addition to capturing single Raman spectra, it is frequently useful to obtain Raman "maps" wherein many spectra are created while moving the sample stage by fractions of a micron. These maps give a better idea of how consistent the properties of nano-scale materials are over small distances.

### Graphene Raman Spectroscopy
Most of my research focuses on graphene, a single atomic layer of carbon atoms arranged in a 2D hexagonal pattern, first isolated by [K.S. Novoselov and A.K. Geim in 2004](https://www.science.org/doi/10.1126/science.1102896).  In my lab, we [synthesize graphene using Chemical Vapor Deposition (CVD)](https://avs.scitation.org/doi/10.1116/1.5144692) and so need a quick, non-destructive method to determine how well (or how poorly) a growth recipe performed. 

The Raman spectrum of graphene consists of [three major peaks (D, G, and 2D)](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.97.187401). The ratio of the intensity of these peaks can tell you a lot about the quality of your graphene. The ratio of the D peak intensity to the G peak intensity provides information about how defective your graphene is (the larger the number, the more defective). The ratio of the 2D peak to the G peak tells you roughly how many layers you have (the larger the number, the fewer the layers). The full width at half-maximum of the 2D peak can also give you information about layer number (the thinner the FWHM, the lower the layer count). The exact location of each peak is useful information as well, as it tell you about lattice stress/strain present in your sample.

The Raman system in [my lab](https://www.pdx.edu/jiao-lab/) is a HORIBA Jobin Yvon HR800, with the 100 mW 532 nm laser typically used for graphene samples.

## GUI Usage
Run the GUI by downloading/cloning this repository, and running the `app.py` file:
```shell
python3 app.py
```

Once the GUI appears, the user must select a file to analyze. This can be accomplished by pressing the "Open" button and navigating to the appropriate file. Once a file is selected, the path will appear in the blank space next to the "Open" button. There is also a drop-down menu to allow for selection of material, this is currently not implemented but in the future the GUI will support further materials.

![gui load](https://github.com/sam-olson/raman-mapper/blob/main/img/gui_load_file.png | width=500)

After a file has been loaded, the user can filter out noisy spectra by providing a signal-to-noise threshold. The signal-to-noise is calculated by taking the standard deviation of a region of the spectrum known to not have peaks (for graphene this is between the G and 2D peaks), and dividing the maximum peak height by this number. The default value is 15, which turns out to do a pretty good job of screening spectra consisting of just noise. If you feel that the algorithm is rejecting good peaks (or you want to know what the bad peaks look like), select the "Save bad spectra?" box, and each rejected spectra will be saved as a .png in the same directory as the map for your review. The filtering function also fits Lorentzians to each peak of non-filtered functions, and removes the baseline, so this can take a bit of time if the data set is large (>5 MB).

![gui filter](https://github.com/sam-olson/raman-mapper/blob/main/img/gui_filtering.png | width=500)

After the data has been filtered appropriately, you can enter relevant information about the growth such as:
- Material 
- Date/time of synthesis
- Growth method
- Further growth details


![gui characteristics](https://github.com/sam-olson/raman-mapper/blob/main/img/gui_characteristics.png | width=500)

These notes will be saved in a text file in the final data directory.

The last area of the default GUI section consists of several checkboxes that allow the user to select which statistics they are interested in collecting from the map. These include:
- Peak ratio heatmaps
- Peak ratio histograms
- Average spectrum (takes average of all spectra and combines it into a single spectrum)
- Peak location heatmaps
- Peak location histograms
- Summary statistics (mean/stdev/max/min of peak ratios/locations)


![gui analysis](https://github.com/sam-olson/raman-mapper/blob/main/img/gui_analysis.png | width=500)

Hit the run button to perform the selected actions, and `raman-mapper` will create a data directory in the same directory as the map. This directory will contain the final results.

If the user selected a heatmap option, a heatmap editing window will appear below the main GUI which will allow the user to make modifications to the heatmaps in real time before saving the final images. Here, the user has the ability to modify several parameters of the heatmap:
- Start/stop value of scalebar
- Start/stop color of scalebar
- Gradient of scalebar (number of colors between min/max)
- Final picture width (the width that the picture will be when saved, in pixels - the height is calculated automatically to preserve aspect ratio)
- Interpolation method for resizing (PIL configs that determine how pixel colors are decided when resizing an image)

The changes can be viewed in real time by pressing the "Update" button. If you wish to keep the same scalebars over many maps for comparison, you may save/load them in a template using the respective buttons (see the `templates` folder for examples). Areas that did not pass the signal-to-noise ratio filter will appear as black in the heatmap

## Data Format
`raman-mapper` is designed to accept Raman map files from HORIBA LabSpec software, in either .txt or .csv formats. The LabSpec software saves the data in a format where the first two columns are the X and Y position of the sample stage, and the first row is the wavenumber (X-axis of each spectrum). Therefore each subsequent row is a unique spectrum, with the XY position given by the first two columns, and the wavenumbers given by the first row. I am unsure if this is industry standard or just how HORIBA saves the results. If you know of a different format, please let me know.

See the `data` folder for an example dataset. 
