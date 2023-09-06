from Process_GPM_Daily import init,  WriteGTiff_daily, calendardays
import datetime
from datetime import timedelta, date
import numpy as np
import os


months = range(1,2)
folder_root = r'D:\Python_Projects\Data\GPM\GPM_3IMERGDF.03'  #Original Not Real Time DataSet
folder_rootRTE = r'D:\Python_Projects\Data\GPM\REAL_TIME\GPM_3IMERGDE.03' #Original EARLY Real Time Dataset
folder_rootRTL = r'D:\Python_Projects\Data\GPM\REAL_TIME\GPM_3IMERGDL.03' #Original LATE Real Time Dataset


for dat in months:
     for year in range(2016,2017):
        initial_date = datetime.date(year, dat, 30)
        ##end_date = datetime.date(year, dat, calendardays(year, month))
        end_date = datetime.date(year, dat, 31)
        dict_matrix = {}
        for kcum in range(date.toordinal(initial_date),date.toordinal(end_date)+1):
            year = str(date.fromordinal(kcum).year)
            if len(str(date.fromordinal(kcum).month))==2:
                month = str(date.fromordinal(kcum).month)
            else:
                month = '0%s' % str(date.fromordinal(kcum).month)
            if len(str(date.fromordinal(kcum).day))==2:
                day = str(date.fromordinal(kcum).day)
            else:
                day = '0%s' % str(date.fromordinal(kcum).day)

            if os.path.exists(r'%s\%s\%s\3B-DAY.MS.MRG.3IMERG.%s%s%s-S000000-E235959.V03.nc4' % (folder_root, year, month, year, month, day)):
                filename = r'%s\%s\%s\3B-DAY.MS.MRG.3IMERG.%s%s%s-S000000-E235959.V03.nc4' % (folder_root, year, month, year, month, day)
                name = 'F'
                RT = 0
            elif os.path.exists(r'%s\%s\%s\3B-DAY-L.MS.MRG.3IMERG.%s%s%s-S000000-E235959.V03.nc4' % (folder_rootRTL, year, month, year, month, day)):
                filename = r'%s\%s\%s\3B-DAY-L.MS.MRG.3IMERG.%s%s%s-S000000-E235959.V03.nc4' % (folder_rootRTL, year, month, year, month, day)
                name = 'L'
                RT = 1
            elif os.path.exists(r'%s\%s\%s\3B-DAY-E.MS.MRG.3IMERG.%s%s%s-S000000-E235959.V03.nc4' % (folder_rootRTE, year, month, year, month, day)):
                filename = r'%s\%s\%s\3B-DAY-E.MS.MRG.3IMERG.%s%s%s-S000000-E235959.V03.nc4' % (folder_rootRTE, year, month, year, month, day)
                name = 'E'
                RT = 1
            else:
                filename = None
                continue
            (matrix,bbox) = init(filename, rt=RT)
            matrix = np.asarray(matrix)
            matrix [matrix < 0] = -99
            dict_matrix[kcum] = matrix
        if dict_matrix == {}:
            continue
        else:
            folder_output = r'D:\Python_Projects\Results\GPM\Cumulated_GPM_Daily\Daily'
            if not os.path.exists(folder_output):
                os.makedirs(folder_output)
            WriteGTiff_daily(dict_matrix,folder_output,'Daily_GPM_%s' % name,bbox['left'],bbox['right'],bbox['bottom'],bbox['top'])
print 'Thank You, Procedure Finished. By W.Camaro'