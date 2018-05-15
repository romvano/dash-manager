#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, 2015 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
"""

from datetime import datetime

def checksum(line):
    """Computes the checksum for the current line.
    """
    check = 0
    for char in line:
        if char.isdigit():
            check += int(char)
        if char == "-":
            check += 1
    return check % 10



def generate_tle(part4):

    p4l = part4.split()
    tle_sp_id = p4l[0][2:] + p4l[1]

    tle_orbit = int(p4l[2]) - 1 # tle start with orbit 0

    epoch = datetime(2000 + int(p4l[4][:2]),
                     int(p4l[4][2:4]),
                     int(p4l[4][4:6]),
                     int(p4l[4][6:8]),
                     int(p4l[4][8:10]),
                     int(p4l[4][10:12]),
                     int(p4l[4][12:15]) * 1000)
    

    tle_epoch = "{0:0.8f}".format(int(epoch.strftime("%y%j")) + (epoch.hour * 60 * 60 + epoch.minute * 60 + epoch.second + epoch.microsecond / 1e6) / (24 * 60 * 60))

    gha = float(p4l[5]) / 10000.0

    tle_ecc = float(p4l[8]) / 100000000.0

    tle_arg_per = float(p4l[9]) / 100000.0

    tle_inclination = float(p4l[11]) / 100000.0

    tle_mean_ano = float(p4l[12]) / 100000.0

    tle_bstar = (float(p4l[20]) / 1e8) * 2.461e-5 * 6378.135/ 2

    l = "{0:1.4e}".format(tle_bstar).replace(".", "").split("e")
    tle_bstar_str = l[0] + str(int(l[1]) + 1)

    tle_bstar = p4l[22] + "0-4"

    tle_mean_mo = int(p4l[26][1:]) * 1e-2 / 360
    if p4l[26][0] == "M":
        tle_mean_mo = -tle_mean_mo
    tle_lon_asc_node = (float(p4l[27]) / 1e5 + gha) % 360






    spids = {"09005A": ("NOAA 19", "33591U"),
             "98030A": ("NOAA 15", "25338U"),
             "05018A": ("NOAA 18", "28654U")  }
    

    tle_dd_mean_motion = ".00000000"
    tle_d_mean_motion = "00000-0"


    line1 = "1 {0:6s} {1:6s}   {2:14s}  {3:s}  {4:s}  {5:7s}  0 999".format(
        spids[tle_sp_id][1],
        tle_sp_id,
        tle_epoch,
        tle_dd_mean_motion,
        tle_d_mean_motion,
        tle_bstar_str)

    line1 = line1 + str(checksum(line1))

    tle_ecc_str = "{0:.7f}".format(tle_ecc)

    line2 = "2 {0:5s} {1:>8.4f} {2:>8.4f} {3:7s} {4:>8.4f} {5:>8.4f} {6:>11.8f}{7:05d}".format(
        spids[tle_sp_id][1][:5],
        tle_inclination,
        tle_lon_asc_node,
        tle_ecc_str[2:],
        tle_arg_per,
        tle_mean_ano,
        tle_mean_mo,
        tle_orbit)

    line2 = line2 + str(checksum(line2))

    return line1, line2





if __name__ == '__main__':
    import urllib2

    daily_tbus_url = "http://noaasis.noaa.gov/cemscs/poltbus.txt"
    fp = urllib2.urlopen(daily_tbus_url)

    tbus = fp.read()
    fp.close()

    items = tbus.split("NNNN\n\n")

    tbuses = []

    for item in items:
        tbus = []
        for line in item.split("\n"):
            clean_line = line.strip()
            if clean_line:
                tbus.append(clean_line)
        tbuses.append(tbus)

    for tbus in tbuses:
        if not tbus:
            continue
        satellite = " ".join(tbus[2].split()[1:])
        for lineno, line in enumerate(tbus):
            if line == "PART IV":
                lineno += 1
                break
        part4 = "\n".join(tbus[lineno:])
        
        lines = generate_tle(part4)
        print satellite
        print lines[0]
        print lines[1]


############### Tests

def test():

    #print "test!"

    part4 = """2009 005A 30983 043018207204 150212002613102 1483008
     01019933 01020490 00138796 16134808 35269969 09897525
     19882771 07228311 P071848002 M009204348 P000000001
     M00158196 M01145249 P07324206 003883805 155154007 9449
     0000500000 M00277416 P00100028 P00508269  20439887           
     020809 M00148 052112 M00885 072709 P00000 000000                    
     APT 137.9125 MHZ, HRPT 1698.0 MHZ, BCN DSB 137.77 MHZ.              
     APT DAY/NIGHT 2,4. VIS CH 2 /0.725 TO 1.0/ AND IR CH 4              
     /10.5 TO 11.5/ XMTD DURING S/C DAY. IR CH3 /3ND IR CH 4             
     /10.5 TO 11.5/ XMTD DURING S/C NIGHT.  DCS CLK TIME                 
     YR/DA/TIM 1995 021 79186.656 LAST TIP CLK CORR 02/08/09.            
     CLK ERR AFTER CORR MINUS 0148 MSEC.  CLK ERR AS OF 05/21/12         
     MINUS 885 MSEC.  ERR RATE AS OF 07/27/09  PLUS 0.0 MS/DAY.          
     NEXT CLK CORR UNKNOWN. N19 APT SWITCH TO VTX1 137.1 MHZ             
     ON 23 JUN 2009 AT 1825Z.                                               
    NNNN"""



    ref_line1 = "1 33591U 09005A   15043.53970792  .00000119  00000-0  89587-4 0  9992"
    ref_line2 = "2 33591  98.9763 353.2216 0014536 157.9967 331.3486 14.11873647309901"

    import numpy as np
    from pyorbital.orbital import Orbital

    orb_ref = Orbital("NOAA 19", line1=ref_line1, line2=ref_line2)
    line1, line2 = generate_tle(part4)
    #print line1
    #print line2
    orb_test = Orbital("NOAA 19", line1=line1, line2=line2)


    from datetime import timedelta
    delta = timedelta(minutes=120)
    epoch = datetime(2015, 2, 12, 0, 26, 13, 102000)
    time = epoch
    cnt = 0
    errors = []
    while cnt < 30:

        #print time
        ref_pos = orb_ref.get_position(time, False)
        test_pos = orb_test.get_position(time, False)

        error = np.sqrt((ref_pos[0][0] - test_pos[0][0])**2 +
                        (ref_pos[0][1] - test_pos[0][1])**2 +
                        (ref_pos[0][2] - test_pos[0][2])**2)
        errors.append(error)


        time = time + delta
        cnt += 1

    #print "max error", np.max(errors), "mean error", np.mean(errors)
    assert(np.max(errors) < 5) #km


test()
