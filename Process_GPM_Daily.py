from osgeo import gdal
import numpy as np
from exceptions import TypeError, ImportError
import os,sys
import datetime
from netCDF4 import Dataset
from datetime import timedelta, date
from osgeo import osr
global bbox_gpm_daily
global cells_degree
global cells_size

bbox_gpm_daily = {
        'top': 90,
        'bottom': -90,
        'left': -180,
        'right': 180
}


"""
General Parameters
"""

cells_size = 0.1
cells_degree = 1/cells_size



def init(filename, bbox=None, rt=None):
    """
    Loads a TRMM data into a matrix. The Open method is set to load the :0 band of the file
    which corresponds to the precipitation data. To load the error switch to the :1.
    """
    ext = os.path.splitext(filename)[-1]
    bbox = checkBbox(bbox)
    reshaped = reshape(filename, ext, rt)
    ##masked = mask(reshaped)
    rearranged = rearrange(reshaped)
    matrix = cut(rearranged, bbox)
    return matrix, bbox


def checkBbox(bbox):
    """
    Returns the correct bbox.
    """
    if not bbox:
        bbox = bbox_gpm_daily
    elif not isinstance(bbox, dict):
        raise TypeError('BBOX must be a dictionary in key: values pairs !!!!')
    return bbox


def reshape(filename, ext, rt=None):
    """
    Opens and reshapes an image file.
    """
    raw_file = Dataset(filename)
    array = raw_file['precipitationCal'][:].data
    array_rot = np.rot90(array)
    right_array = array_rot[:, 1800:]
    left_array = array_rot[:, :1800]
    reversed_array = np.hstack((right_array, left_array))
    if rt == 1:
        reversed_array = reversed_array[40:440]
    return reversed_array


def mask(matrix):
    """
    Applies a mask to image in order to remove the water cells.

    """
    mask_image = r'D:\Python_Projects\Data\TRMM\Mask_image\trmm_land_sea_wide_bin.png'
    img = Image.open(mask_image)
    imgarray = np.array(img)
    matrix = np.array(matrix)
    masked = matrix / imgarray
    return masked


def rearrange(matrix):
    b = np.split(matrix, 2, axis=1)[0]
    a = np.split(matrix, 2, axis=1)[1]
    rearranged = np.concatenate((a, b), axis=1)
    return rearranged


def cut(raw_matrix, bbox):
    """
    Fuction for slicing the given matrix based on the passed bounding box

    """

    bbox_matrix = bbox_gpm_daily
    cell_bbox_size = {
        'x': abs(bbox['left'] - bbox['right']) * cells_degree,
        'y': abs(bbox['top'] - bbox['bottom']) * cells_degree
    }
    slice_start = {
        'x': abs(bbox_matrix['left'] - bbox['left']) * cells_degree,
        'y': abs(bbox_matrix['top'] - bbox['top']) * cells_degree
    }
    slice_end = {
        'x': slice_start['x'] + cell_bbox_size['x'],
        'y': slice_start['y'] + cell_bbox_size['y'],
    }
    matrix_sliced_y = raw_matrix[slice_start['y']:slice_end['y']]
    matrix_sliced = [row[slice_start['x']:slice_end['x']] for row in matrix_sliced_y]
    return matrix_sliced

def calendardays(year,month):
    if (year % 4 == 0 and not year % 100 == 0)or year % 400 == 0:
        days = [31,29,31,30,31,30,30,31,30,31,30,31]
    else:
        days = [31,28,31,30,31,30,30,31,30,31,30,31]
    return days[month-1]


def WriteGTiff_daily(dict_x,folder,name,xmin,xmax,ymin,ymax):
    """
    Write a Gtiff, from a dictionary (Elements = Numpy Array type) defining each
    element from the dictionary like a Raster.
    """
    gdal.AllRegister()
    driver = gdal.GetDriverByName('Gtiff')
    nrows,ncols = np.shape(dict_x[dict_x.keys()[0]])
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform = (xmin,xres,0,ymax,0,-yres)
    for kcum in dict_x.keys():
        endd = date.fromordinal(kcum)
        if len(str(endd.day))==1:
            end_day = '0%s' %str(endd.day)
        else:
            end_day = str(endd.day)
        if len(str(endd.month))==1:
            end_month = '0%s' %str(endd.month)
        else:
            end_month = str(endd.month)
        end_date = '%s%s%s' %(endd.year,end_month,end_day)
        filename = r'%s/GPM_%s_%s.tif' % (folder,name,end_date)
        outDataset = driver.Create(filename,ncols,nrows,1,gdal.GDT_Float32)
        outDataset.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        outDataset.SetProjection(srs.ExportToWkt())
        nband = 1
        array = np.empty([nrows,ncols])
        array = dict_x[kcum]
        array[np.isnan(array)] = -99
        array[np.isinf(array)] = -99
        outband = outDataset.GetRasterBand(nband)
        outband.SetNoDataValue(-99)
        outband.WriteArray(array)
        outband.GetStatistics(0,1)
        outband = None
        outDataset = None