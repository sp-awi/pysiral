# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 13:57:56 2016

@author: Stefan

Important Note:

    All sic data handlers must be subclasses of pysiral.auxdata.AuxdataBaseClass in order to work
    for the Level-2 Processor. If the auxiliary class is based on a static dataset, this should be parsed
    in `__init__`.

    Please review the variables and properties in the parent class, as well as the correspodning config and
    support classes for grid track interpolation in the pysiral.auxdata module for additional guidance.

    The only other hard requirements is the presence of on specific method in order to be a valid subclass of
    AuxdataBaseClass:


        get_l2_track_vars(l2)

            This method will be called during the Level-2 processor. The argument is the Level-2 data object and
            the purpose of the method is to compute the auxilary variable(s) and associated uncertainty. These
            variable need to be registered using the `register_auxvar(id, name, value, uncertainty)` method of
            the base class. All sic subclasses need to register at minimum the following variable:

                sea ice concentration (in percent):
                    id: sic
                    name: sea_ice_concentration

            e.g., this code line is mandatory for `get_l2_track_vars` (uncertainty can be None):

                # Register Variables
                self.register_auxvar("sic", "sea_ice_concentration", value, uncertainty)

"""


from pysiral.l2data import Level2Data
from pysiral.auxdata import AuxdataBaseClass, GridTrackInterpol
from pysiral.iotools import ReadNC


import scipy.ndimage as ndimage
from pyproj import Proj
import numpy as np
from pathlib import Path
from typing import List


class OsiSafSIC(AuxdataBaseClass):
    """ A class for Sea Ice Concentration data from OSI-SAF """

    def __init__(self, *args, **kwargs) -> None:
        """
        Init the class.
        NOTE: The options template can be different for continuous data sets (is_cdr_icdr: False)
              and those with a dedicated split into a climate data record (cdr) and an interim
              climate data record (icdr). A pre-processing of the options dictionary is therefore necessary
              to follow the mechanics of the auxiliary data class.
        :param args:
        :param kwargs:
        """

        # Pre-process the options for cdr/icdr data sets
        cfg = args[0]
        is_cdr_icdr = cfg.options.get("is_cdr_icdr", False)
        target_version = cfg.options.get("version", None)
        if is_cdr_icdr:
            global_options = cfg.options.get("global", {})
            version_options = cfg.options.get(target_version, {})
            cfg.options.update(global_options)
            cfg.options.update(version_options)
            cfg.options.update({"long_name_template": cfg.long_name})
        super(OsiSafSIC, self).__init__(*args, **kwargs)

        # Class properties
        self._data = None
        self.start_time = None
        self.hemisphere_code = None

    def get_l2_track_vars(self, l2: "Level2Data") -> None:
        """
        Main entry point of the class, add sea ice concentration to the l2 data object (in-place)
        :param l2: Level-2 data object<
        :return: None
        """

        # These properties are needed to construct the product path
        self.start_time = l2.info.start_time
        self.hemisphere_code = l2.hemisphere_code

        # Set the requested date
        self.set_requested_date_from_l2(l2)

        # Update the external data
        self.update_external_data()

        # Check if error with file I/O
        if self.error.status or self._data is None:
            sic = self.get_empty_array(l2)
        else:
            # Get and return the track
            sic = self._get_sic_track(l2)

            # Fill pole hole
            if "fill_pole_hole" in self.cfg.options:
                opt = self.cfg.options.fill_pole_hole
                is_near_pole_hole = l2.track.latitude >= opt.pole_hole_lat_threshold
                indices = np.where(np.logical_and(is_near_pole_hole, np.isnan(sic)))
                sic[indices] = opt.pole_hole_fill_value

        # All done, register the variable
        self.register_auxvar("sic", "sea_ice_concentration", sic, None)

    def load_requested_auxdata(self) -> None:
        """
        Required subclass method: Load the data file necessary to satisfy condition for requested date
        :return:
        """

        # Retrieve the file path for the requested date from a property of the auxdata parent class
        path = Path(self.requested_filepath)

        #  --- Validation ---
        if not path.is_file():
            msg = self.pyclass+": File not found: %s " % path
            self.add_handler_message(msg)
            self.error.add_error("auxdata_missing_sic", msg)
            return

        # --- Read the data ---
        self._data = ReadNC(path)

        # --- Pre-process the data ---
        # Remove time dimension
        self._data.ice_conc = self._data.ice_conc[0, :, :]

        # No negative ice concentrations
        flagged = np.where(self._data.ice_conc < 0)
        self._data.ice_conc[flagged] = np.nan

    def _get_sic_track(self, l2: "Level2Data") -> np.ndarray:
        """
        Simple extraction along trajectory
        :param l2:
        :return: sea ice concentration array
        """

        # Extract from grid
        griddef = self.cfg.options[l2.hemisphere]
        grid_lons, grid_lats = self._data.lon, self._data.lat
        grid2track = GridTrackInterpol(l2.track.longitude, l2.track.latitude, grid_lons, grid_lats, griddef)
        sic = grid2track.get_from_grid_variable(self._data.ice_conc, flipud=True)

        return sic

    @property
    def requested_filepath(self) -> "Path":
        """
        Note: this overwrites the property in the super class due to some
        peculiarities with the filenaming (auto product changes etc)
        :return: The filepath to the target file
        """

        # The path needs to be completed if two products shall be used
        opt = self.cfg.options

        # For data records that consists of cdr/icdr only: Check if in cdr or icdr period
        # This also affects the long_name of the data set which is updated here
        is_cdr_icdr = opt.get("is_cdr_icdr", False)
        version = opt.get("version", None)
        record_type = None
        if is_cdr_icdr:
            product_index = int(self.start_time > opt[opt.version]["cdr_time_coverage_end"])
            record_type = self.cdr_icdr_record_types[product_index]
            record_type_prefix = self.cdr_icdr_record_type_prefix[product_index]
            long_name_template = opt.get("long_name_template", {})
            long_name = long_name_template.format(record_type_prefix=record_type_prefix, version=version)
            self.cfg.set_long_name(long_name)

        # Get the file path
        # Paths for climate data records should contain record type and version
        path = Path(self.cfg.local_repository)
        if is_cdr_icdr:
            path = path / record_type / version

        # Add period sub-folders as indicated
        for subfolder_tag in self.cfg.subfolders:
            subfolder = getattr(self, subfolder_tag)
            path = path / subfolder

        # Construct the filename
        filename = self.cfg.filenaming.format(
            record_type=record_type,
            version=version,
            year=self.year,
            month=self.month,
            day=self.day,
            hemisphere_code=self.hemisphere_code)

        # Final Path
        path = path / filename
        return path

    @property
    def cdr_icdr_record_types(self) -> List[str]:
        return ["cdr", "icdr"]

    @property
    def cdr_icdr_record_type_prefix(self) -> List[str]:
        return ["", "interim"]


class IfremerSIC(AuxdataBaseClass):

    def __init__(self, *args, **kwargs):

        super(IfremerSIC, self).__init__(*args, **kwargs)
        self._data = None

        # XXX: This is a dirty hack, but needed for getting SIC lon/lat grid
        self._grid = {}
        for hemisphere in ["north", "south"]:
            grid_file = Path(self.cfg.local_repository) / "grid_%s_12km.nc" % hemisphere
            self._grid[hemisphere] = ReadNC(grid_file)

    def get_l2_track_vars(self, l2):
        self._get_requested_date(l2)
        self._get_data(l2)
        sic = self._get_sic_track(l2)
        # All done, register the variable
        self.register_auxvar("sic", "sea_ice_concentration", sic, None)

    def _get_requested_date(self, l2):
        """ Use first timestamp as reference, date changes are ignored """
        year = l2.track.timestamp[0].year
        month = l2.track.timestamp[0].month
        day = l2.track.timestamp[0].day
        self._requested_date = [year, month, day]

    def _get_data(self, l2):
        """ Loads file from local repository only if needed """
        if self._requested_date == self._current_date:
            # Data already loaded, nothing to do
            return
        path = Path(self._get_local_repository_filename(l2))

        # Validation
        if not path.is_file():
            msg ="IfremerSIC: File not found: %s " % path
            self.add_handler_message(msg)
            self.error.add_error("auxdata_missing_sic", msg)
            return

        self._data = ReadNC(path)
        self._data.ice_conc = self._data.concentration[0, :, :]
        flagged = np.where(np.logical_or(self._data.ice_conc < 0, self._data.ice_conc > 100))
        self._data.ice_conc[flagged] = 0

        # This step is important for calculation of image coordinates
        self._data.ice_conc = np.flipud(self._data.ice_conc)
        self.add_handler_message("IfremerSIC: Loaded SIC file: %s" % path)
        self._current_date = self._requested_date

    def _get_local_repository_filename(self, l2):
        path = Path(self.cfg.local_repository)
        for subfolder_tag in self.cfg.subfolders:
            subfolder = getattr(self, subfolder_tag)
            path = path / subfolder
        filename = self.cfg.filenaming.format(
            year=self.year, month=self.month, day=self.day,
            hemisphere_code=l2.hemisphere_code)
        path = path / filename
        return path

    def _get_sic_track(self, l2):
        # Convert grid/track coordinates to grid projection coordinates
        kwargs = self.cfg.options[l2.hemisphere].projection
        p = Proj(**kwargs)
        grid = self._grid[l2.hemisphere]
        x, y = p(grid.longitude, grid.latitude)
        l2x, l2y = p(l2.track.longitude, l2.track.latitude)
        # Convert track projection coordinates to image coordinates
        # x: 0 < n_lines; y: 0 < n_cols
        dim = self.cfg.options[l2.hemisphere].dimension
        x_min = x[dim.n_lines-1, 0]
        y_min = y[dim.n_lines-1, 0]
        ix, iy = (l2x-x_min)/dim.dx, (l2y-y_min)/dim.dy
        # Extract along track data from grid
        sic = ndimage.map_coordinates(self._data.ice_conc, [iy, ix], order=0)
        return sic
