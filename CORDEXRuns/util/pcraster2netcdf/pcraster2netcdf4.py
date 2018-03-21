#! /usr/bin/python

__author__="Gomes G."
__date__ ="$Feb 19, 2016 16:16:00$"
__version__ ="1.0"

import numpy as np
from netCDF4 import Dataset
import time as timex
import sys, os, glob
import ConfigParser
from numpy import loadtxt


__OUTPUT_FILE_EXT = '.nc'
__MAP2ASC_CMD = '/software/PCRaster/pcraster4/bin/map2asc'
__TEMP_FILE_SUFIX = '_temp.txt'

__NETCDF_DATASET_FORMAT = 'NETCDF4_CLASSIC'
__NETCDF_CONVENTIONS = 'CF-1.6'
__NETCDF_SOURCE_SOFTWARE = 'Python netCDF4'

__NETCDF_VAR_TIME_DIMENSION = None
__NETCDF_VAR_TIME_CALENDAR_TYPE = 'proleptic_gregorian'

__NETCDF_VAR_DATA_TYPE = 'f8'
__NETCDF_VALUE_DATA_TYPE = 'f4'
__NETCDF_COORDINATES_DATA_TYPE = 'i4'

__KEY_STANDARD_NAME = 'value_standard_name'
__KEY_LONG_NAME = 'value_long_name'
__KEY_UNIT = 'value_unit'

__meteo_vars_config = {
    'pr' : {__KEY_UNIT : 'mm', __KEY_STANDARD_NAME : 'pr', __KEY_LONG_NAME : 'precipitation'},
    'tn' : {__KEY_UNIT : 'celcius', __KEY_STANDARD_NAME : 'tn', __KEY_LONG_NAME : 'min_temperature'},
    'tx' : {__KEY_UNIT : 'celcius', __KEY_STANDARD_NAME : 'tx', __KEY_LONG_NAME : 'max_temperature'},
    'ta' : {__KEY_UNIT : 'celcius', __KEY_STANDARD_NAME : 'ta', __KEY_LONG_NAME : 'avg_temperature'},
    'ws' : {__KEY_UNIT : 'm/s', __KEY_STANDARD_NAME : 'ws', __KEY_LONG_NAME : 'avg_wind_speed'},
    'pd' : {__KEY_UNIT : 'hPa', __KEY_STANDARD_NAME : 'pd', __KEY_LONG_NAME : 'avg_vapor_pressure'},
    'rg' : {__KEY_UNIT : 'KJ/m2/day', __KEY_STANDARD_NAME : 'rg', __KEY_LONG_NAME : 'calculated_radiation'},
    'e0' : {__KEY_UNIT : 'mm', __KEY_STANDARD_NAME : 'e0', __KEY_LONG_NAME : 'pot_evaporation_water'},
    'et' : {__KEY_UNIT : 'mm', __KEY_STANDARD_NAME : 'et', __KEY_LONG_NAME : 'pot_evaporation_reference_crop'},
    'es' : {__KEY_UNIT : 'mm', __KEY_STANDARD_NAME : 'es', __KEY_LONG_NAME : 'pot_evaporation_moist'}
}

configFile = ConfigParser.ConfigParser()

def openwritenetcdf(nf2, var_name):
    # General Attributes
    nf2.history = 'Created ' + timex.ctime(timex.time())
    nf2.Conventions = __NETCDF_CONVENTIONS
    nf2.Source_Software = __NETCDF_SOURCE_SOFTWARE
    nf2.reference = configFile.get('GENERIC','NETCDF_REFERENCE')
    nf2.title = configFile.get('GENERIC','NETCDF_TITLE')
    nf2.keywords = configFile.get('GENERIC','NETCDF_KEYWORDS')
    nf2.source = configFile.get('GENERIC','NETCDF_SOURCE')
    nf2.institution = configFile.get('GENERIC','NETCDF_INSTITUTION')

    netcdf_var_x = configFile.get('VAR_X','NAME')
    netcdf_var_y = configFile.get('VAR_Y','NAME')
    netcdf_var_time = configFile.get('VAR_TIME','NAME')

    #Dimension
    nf2.createDimension(netcdf_var_x, int(configFile.get('DIMENSION','COLUMNS')))
    nf2.createDimension(netcdf_var_y, int(configFile.get('DIMENSION','ROWS')))
    nf2.createDimension(netcdf_var_time, __NETCDF_VAR_TIME_DIMENSION)

    #Variables
    longitude = nf2.createVariable(netcdf_var_x, __NETCDF_VAR_DATA_TYPE, (netcdf_var_x))
    latitude = nf2.createVariable(netcdf_var_y, __NETCDF_VAR_DATA_TYPE, (netcdf_var_y))
    time = nf2.createVariable(netcdf_var_time, __NETCDF_VAR_DATA_TYPE, (netcdf_var_time))

    longitude.standard_name= configFile.get('VAR_X','STANDARD_NAME')
    longitude.long_name= configFile.get('VAR_X','LONG_NAME')
    longitude.units = configFile.get('VAR_X','UNIT')

    latitude.standard_name= configFile.get('VAR_Y','STANDARD_NAME')
    latitude.long_name= configFile.get('VAR_Y','LONG_NAME')
    latitude.units = configFile.get('VAR_Y','UNIT')

    time.standard_name = configFile.get('VAR_TIME','STANDARD_NAME')
    time.units = configFile.get('VAR_TIME','UNIT')
    time.frequency = configFile.get('VAR_TIME','FREQUENCY')
    time.calendar = __NETCDF_VAR_TIME_CALENDAR_TYPE

    proj = nf2.createVariable(configFile.get('PROJECTION','GRID_MAPPING'), __NETCDF_COORDINATES_DATA_TYPE)
    proj.grid_mapping_name = configFile.get('PROJECTION','GRID_MAPPING')
    proj.false_easting = float(configFile.get('PROJECTION','FALSE_EASTING'))
    proj.false_northing = float(configFile.get('PROJECTION','FALSE_NORTHING'))
    proj.longitude_of_projection_origin = float(configFile.get('PROJECTION','ORIGIN_LONGITUDE'))
    proj.latitude_of_projection_origin = float(configFile.get('PROJECTION','ORIGIN_LATITUDE'))
    proj.semi_major_axis = float(configFile.get('PROJECTION','SEMI_MAJOR_AXIS'))
    proj.inverse_flattening = float(configFile.get('PROJECTION','INVERSE_FLATTENING'))
    proj.proj4_params = configFile.get('PROJECTION','PARAMS')
    proj.EPSG_code = configFile.get('PROJECTION','EPSG_CODE')

    value = nf2.createVariable(var_name, __NETCDF_VALUE_DATA_TYPE, (netcdf_var_time, netcdf_var_y, netcdf_var_x), zlib=True, complevel=9, least_significant_digit=2)
    value.standard_name = __meteo_vars_config[var_name][__KEY_STANDARD_NAME]
    value.long_name = __meteo_vars_config[var_name][__KEY_LONG_NAME]
    value.units = __meteo_vars_config[var_name][__KEY_UNIT]
    
    value.grid_mapping = configFile.get('PROJECTION','GRID_MAPPING')
    value.esri_pe_string = configFile.get('PROJECTION','STRING')
    
    grid_cell_size = int(configFile.get('DIMENSION','CELL_SIZE'))
    # lats.shape, lons.shape
    latitude[:] = np.arange(int(configFile.get('DIMENSION','TOP')), int(configFile.get('DIMENSION','BOTTOM')), -1 * grid_cell_size)    #y  Europe
    longitude[:] = np.arange(int(configFile.get('DIMENSION','LEFT')), int(configFile.get('DIMENSION','RIGHT')), grid_cell_size)    #x  Europe

def generate_map2asc_command(pcraster_filename, temp_filename):
    return __MAP2ASC_CMD + ' ' + pcraster_filename + ' ' + temp_filename # + ' >/dev/null 2>&1'

# ------------------------------------
# MAIN: create a single netcdf file from a stack of PCRaster maps
# ============================================
# ============================================

def main(argv):
    vars_list = ' | '.join(__meteo_vars_config.keys())
    help_str = '\nThis script merges into a single NETCDF4 file all daily PCRaster files from a single variable generated by 2Map script.\n\nUsage: python pcraster2netcdf4.py {'+vars_list+'} <config_file> <output_folder> <input_folder>'
    if len(argv) == 4:
        var_name = argv[0]
        configFile.read(argv[1])
        netcdf_var_time = configFile.get('VAR_TIME','NAME')
        if var_name in __meteo_vars_config:
            outbasedir = os.path.normpath(argv[2])
            inbasedir = os.path.normpath(argv[3])
            
            outName=os.path.join(outbasedir, var_name+__OUTPUT_FILE_EXT)
            
            print 'Start generating netcdf file for variable: '+ var_name
            print 'input folder: ' + inbasedir
            print 'netcdf output file: ' + outName
            
            # ------- open netcdfs for writing
            nf2 = Dataset(outName, 'w', format=__NETCDF_DATASET_FORMAT)
            openwritenetcdf(nf2, var_name)
            
            inputWildcards = os.path.join(inbasedir,var_name+configFile.get('GENERIC','INPUT_WILDCARD'))
            print 'Start loading files using the wildcard: ' + inputWildcards
            
            tempfilename = os.path.join(outbasedir, var_name+__TEMP_FILE_SUFIX)
            time_frequency = int(configFile.get('VAR_TIME','FREQUENCY'))
            k=0
            for f in sorted(glob.glob(inputWildcards)):
                basepath, filename = os.path.split(f)
                print 'Loading file: '+ filename
                # print 'Loading file: '+ f[-12:] # et000000.001
                os.system( generate_map2asc_command(f, tempfilename) )
                value = loadtxt(tempfilename)
                value[value==1e31] = np.nan
                nf2.variables[netcdf_var_time][k] = k * time_frequency
                nf2.variables[var_name][k, :, :] = value
                os.remove(tempfilename)
                k += 1
            
            print 'Finished generating the netcdf file containing ' + str(k * time_frequency) + ' ' + configFile.get('VAR_TIME','UNIT') + '.'
            
            nf2.close()
            
            print 'Closed netcdf output file: ' + outName
        else:
            print 'ERROR: Unknown variable, script is expecting one of {'+vars_list+'}.\n' + help_str
    else:
        print help_str
        
if __name__ == '__main__':
    main(sys.argv[1:])

