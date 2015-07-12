# -*- coding=utf-8 -*-
"""
Created on Fri Jul 10 21:00:37 2015

@author=Stefan
"""

from collections import namedtuple
import struct


class Cryosat2L1bMSDDefinitionSarBaselineC(object):
    """ Holds the Definition of L1b MDS records """

    def __init__(self):

        # This definition holds the following msd fields:
        self.msd_groups = [
            "time_orbit_group",
            "measurement_group",
            "geocorrections_group",
            "onehz_wavefrom_group",
            "waveform_group"]

        # Default definition of fields
        mds_def = namedtuple('mds_def', ['name', 'fmt', 'size'])

        self.time_orbit_group = [
            mds_def(name="day", fmt="L", size=4),
            mds_def(name="sec", fmt="l", size=4),
            mds_def(name="msec", fmt="l", size=4),
            mds_def(name="uso_corr", fmt="l", size=4),
            mds_def(name="mode_id", fmt="H", size=2),
            mds_def(name="source_sequence_counter", fmt="H", size=2),
            mds_def(name="instrument_configuration", fmt="L", size=4),
            mds_def(name="burst_counter", fmt="L", size=4),
            mds_def(name="measurement_latitude", fmt="l", size=4),
            mds_def(name="measurement_longtitude", fmt="l", size=4),
            mds_def(name="altitude_cog", fmt="L", size=4),
            mds_def(name="altitude_rate", fmt="L", size=4),
            mds_def(name="satellite_velocity", fmt="(3l)", size=12),
            mds_def(name="real_beam", fmt="(3L)", size=12),
            mds_def(name="interferometry_baseline", fmt="(3l)", size=12),
            mds_def(name="star_tracker_usage", fmt="H", size=2),
            mds_def(name="antenna_roll", fmt="l", size=4),
            mds_def(name="antenna_pitch", fmt="l", size=4),
            mds_def(name="antenna_yaw", fmt="l", size=4),
            mds_def(name="fbr_confidence_flag", fmt="l", size=4),
            mds_def(name="spare", fmt="4c", size=4)]

        # measurement group
        self.measurement_group = [
            mds_def(name="td", fmt="q", size=8),
            mds_def(name="h0", fmt="l", size=4),
            mds_def(name="cor2", fmt="l", size=4),
            mds_def(name="lai", fmt="l", size=4),
            mds_def(name="fai", fmt="l", size=4),
            mds_def(name="agc_ch1", fmt="l", size=4),
            mds_def(name="agc_ch2", fmt="l", size=4),
            mds_def(name="tr_gain_ch1", fmt="l", size=4),
            mds_def(name="tr_gain_ch2", fmt="l", size=4),
            mds_def(name="tx_power", fmt="l", size=4),
            mds_def(name="dopp_rc", fmt="l", size=4),
            mds_def(name="tr_inst_rc", fmt="l", size=4),
            mds_def(name="r_inst_rc", fmt="l", size=4),
            mds_def(name="tr_inst_gain_c", fmt="l", size=4),
            mds_def(name="r_inst_gain_c", fmt="l", size=4),
            mds_def(name="int_phase_c", fmt="l", size=4),
            mds_def(name="ext_phase_c", fmt="l", size=4),
            mds_def(name="noise_pwr", fmt="l", size=4),
            mds_def(name="phase_slope_c", fmt="l", size=4),
            mds_def(name="spares", fmt="4b", size=4)]

        # Geocorrections group
        self.geocorrections_group = [
            mds_def(name="dry_c", fmt="l", size=4),
            mds_def(name="wet_c", fmt="l", size=4),
            mds_def(name="ib_c", fmt="l", size=4),
            mds_def(name="dac_c", fmt="l", size=4),
            mds_def(name="iono_gim", fmt="l", size=4),
            mds_def(name="iono_mod", fmt="l", size=4),
            mds_def(name="h_ot", fmt="l", size=4),
            mds_def(name="h_lpeot", fmt="l", size=4),
            mds_def(name="h_olt", fmt="l", size=4),
            mds_def(name="h_set", fmt="l", size=4),
            mds_def(name="h_gpt", fmt="l", size=4),
            mds_def(name="surf_type", fmt="L", size=4),
            mds_def(name="spare1", fmt="4b", size=4),
            mds_def(name="corr_status", fmt="L", size=4),
            mds_def(name="corr_error", fmt="L", size=4),
            mds_def(name="spare2", fmt="4b", size=4)]

        # 1Hz Average SAR Waveform group
        self.onehz_waveform_group = [
            mds_def(name="day_1hz", fmt="l", size=4),
            mds_def(name="sec_1hz", fmt="L", size=4),
            mds_def(name="micsec_1hz", fmt="L", size=4),
            mds_def(name="lat_1hz", fmt="l", size=4),
            mds_def(name="lon_1hz", fmt="l", size=4),
            mds_def(name="alt_1hz", fmt="l", size=4),
            mds_def(name="td_1hz", fmt="q", size=8),
            mds_def(name="avg_wfm", fmt="512H", size=1024),
            mds_def(name="linear_wfm_mult", fmt="l", size=4),
            mds_def(name="power2_wfm_mult", fmt="l", size=4),
            mds_def(name="num_avg_echoes", fmt="H", size=2),
            mds_def(name="flags", fmt="H", size=2)]

        # 20 Hz SAR Waveform group
        self.waveform_group = [
            mds_def(name="wfm", fmt="256H", size=512),
            mds_def(name="linear_wfm_multiplier", fmt="l", size=4),
            mds_def(name="power2_wfm_multiplier", fmt="l", size=4),
            mds_def(name="num_avg_echoes", fmt="H", size=2),
            mds_def(name="flags", fmt="H", size=2),
            mds_def(name="beam", fmt="100b", size=100)]


#            mds_def(name="beam_sd", fmt="H", size=2),
#            mds_def(name="beam_centre", fmt="H", size=2),
#            mds_def(name="beam_amplitude", fmt="H", size=2),
#            mds_def(name="beam_skew", fmt="h", size=2),
#            mds_def(name="beam_kurt", fmt="h", size=2),
#            mds_def(name="beam_spare", fmt="50b", size=50)]

    def get_bytesize(self, msd_group):
        group = getattr(self, msd_group)
        return sum([field.size for field in group])

    def get_struct_parser(self, msd_group):
        group = getattr(self, msd_group)
        return ">"+"".join([field.fmt for field in group])

    def get_field_names(self, msd_group):
        group = getattr(self, msd_group)
        return ([field.name for field in group])


def cryosat2_get_msd_def(radar_mode, baseline):
    # XXX: Testing purposes only, needs functionality
    return Cryosat2L1bMSDDefinitionSarBaselineC()
