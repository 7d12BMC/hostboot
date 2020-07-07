# IBM_PROLOG_BEGIN_TAG
# This is an automatically generated prolog.
#
# $Source: src/build/simics/eecache-gen.py $
#
# OpenPOWER HostBoot Project
#
# Contributors Listed Below - COPYRIGHT 2020
# [+] International Business Machines Corp.
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
#
# IBM_PROLOG_END_TAG
###############################
## Generate EECACHE partition
##
## Hostboot needs a way to grab image objects to create eecache for them
## to read contents directly out of a file rather than going to the
## device(which is very slow).  The way eecache is setup is to have a header
## and all the VPD images they care about (they may not need all the images,
## but they will pick and choose using the commands simics provides
## .. get-seeprom and get-dimm-seeprom) and put them in a predefined structure
## with information on its offset (mainly VPD, like MVPD for proc 1 on DCM0 or
## MVPD for proc 1 in DCM1 on rainier)
##
###############################
import os
import cli
import struct

###########################################################################
# version 1 header record
###########################################################################
def write_eecache_record_v1(f, huid, port, engine, addr, mux, size, offset, valid):
    f.write(struct.pack('>i', huid));
    f.write(struct.pack('>B', port));
    f.write(struct.pack('>B', engine));
    f.write(struct.pack('>B', addr));
    f.write(struct.pack('>B', mux));
    f.write(struct.pack('>i', size));
    f.write(struct.pack('>I', offset));
    f.write(struct.pack('>B', valid));
    return

###########################################################################
# version 2 header records
###########################################################################
def write_spi_eecache_record(f, huid, engine, offset_KB, size, offset, valid):
    f.write(struct.pack('>B', 0x02)); # 0x02 = SPI access
    f.write(struct.pack('>i', huid));
    f.write(struct.pack('>B', engine));
    f.write(struct.pack('>H', offset_KB));
    f.write(struct.pack('>B', 0x00));
    f.write(struct.pack('>i', size));
    f.write(struct.pack('>I', offset));
    f.write(struct.pack('>B', valid));
    return

def write_i2c_eecache_record(f, huid, port, engine, devAddr, mux, size, offset, valid):
    f.write(struct.pack('>B', 0x01)); # 0x01 = I2C access
    f.write(struct.pack('>i', huid));
    f.write(struct.pack('>B', port));
    f.write(struct.pack('>B', engine));
    f.write(struct.pack('>B', devAddr));
    f.write(struct.pack('>B', mux));
    f.write(struct.pack('>i', size));
    f.write(struct.pack('>I', offset));
    f.write(struct.pack('>B', valid));
    return

###########################################################################
##
## hb_eecache_setup - fills in the eecache file with header and vpd content
#
# See eeprom_const.H for header information
# Version 1 only supports i2c
# Version 2a - changes version 1 to version 2 (intermediate, just i2c)
# Version 2 supports i2c and spi access (adds another byte to header size)
#
###########################################################################
def hb_eecache_setup(file_name, version, verbose):

    # create the header records
    with open(file_name, 'wb') as f:
        if version == 1:
            # version, written in 1 byte. only supports version 1
            f.write(struct.pack('>B', 1));
            # end of cache, written in 4 bytes
            f.write(struct.pack('>i', 0x24357));

            # eepromRecordHeader for MVPD (proc 0)
            write_eecache_record_v1(f, 0x50000, 0, 1, 0xA0, 0xFF, 64, 0x357, 0x80);
            # for DIMM port 0
            write_eecache_record_v1(f, 0x50000, 9, 3, 0xA0, 0xFF, 4, 0x10357, 0x80);
            # for DIMM port 1
            write_eecache_record_v1(f, 0x50000, 8, 3, 0xA0, 0xFF, 4, 0x11357, 0x80);

            # eepromRecordHeader for MVPD (proc 1)
            write_eecache_record_v1(f, 0x50001, 0, 1, 0xA0, 0xFF, 64, 0x12357, 0x80);
            # for DIMM port 0
            write_eecache_record_v1(f, 0x50001, 9, 3, 0xA0, 0xFF, 4,  0x22357, 0x80);
            # for DIMM port 1
            write_eecache_record_v1(f, 0x50001, 8, 3, 0xA0, 0xFF, 4,  0x23357, 0x80);

            # Note: These max eeprom counts come from src/include/usr/eeprom/eeprom_const.H
            # For version 1, it is currently a max count of 50
            # Given 6 records already filled out above, 44 more record headers
            # can be filled out as empty
            for _ in range(44):
                write_eecache_record_v1(f, 0, 0, 0, 0, 0, 0, 0xFFFFFFFF, 0);

        elif version == 2:
            # version, written in 1 byte. (version 2 but no SPI access yet)
            f.write(struct.pack('>B', 2));
            # end of cache, written in 4 bytes
            f.write(struct.pack('>i', 0x1270D));

            # eepromRecordHeader for MVPD (proc 0)
            write_i2c_eecache_record(f, 0x50000, 0, 1, 0xA0, 0xFF, 64, 0x70D, 0xC0);
            # for DIMM port 0
            write_i2c_eecache_record(f, 0x50000, 0, 3, 0xA0, 0xFF, 4, 0x1070D, 0xC0);
            # for DIMM port 1
            write_i2c_eecache_record(f, 0x50000, 1, 3, 0xA0, 0xFF, 4, 0x1170D, 0xC0);

            # Note: These max eeprom counts come from src/include/usr/eeprom/eeprom_const.H
            # For version 2, it is currently a max count of 100
            # Given 3 records already filled out above, 97 more record headers
            # can be filled out as empty
            for _ in range(97):
                write_i2c_eecache_record(f, 0, 0, 0, 0, 0, 0, 0xFFFFFFFF, 0);

        else:
            # version, written in 1 byte. Supports version 2 with SPI
            f.write(struct.pack('>B', 2));
            # end of cache, written in 4 bytes
            f.write(struct.pack('>i', 0x1270D));
            # eepromRecordHeader for MVPD
            write_spi_eecache_record(f, 0x50000, 0x02, 0x00C0, 64, 0x70D, 0xC0);
            # for DIMM port 0
            write_i2c_eecache_record(f, 0x50000, 0, 3, 0xA0, 0xFF, 4, 0x1070D, 0xC0);
            # for DIMM port 1
            write_i2c_eecache_record(f, 0x50000, 1, 3, 0xA0, 0xFF, 4, 0x1170D, 0xC0);

            # Note: These max eeprom counts come from src/include/usr/eeprom/eeprom_const.H
            # For version 2, it is currently a max count of 100
            # Given 3 records already filled out above, 97 more record headers
            # can be filled out as empty
            for _ in range(97):
                write_i2c_eecache_record(f, 0, 0, 0, 0, 0, 0, 0xFFFFFFFF, 0);

    ##################################### Populate Proc 0 Records ####################################
    # now add 64K mvpd record for processor 0 (0x50000)
    ret = cli.run_command("get-seeprom 0 0 2") # reading MVPD

    if ret != None:
        # simics object for the image
        image = simics.SIM_get_object(ret)
        # string of bytes from simics interface
        read_buf = image.iface.image.get(0x30000, 0x10000) # interface takes start and length

        # Probably this file will be deleted once we write to BMC
        with open(file_name, 'ab') as f:
            f.write(read_buf)

    # now add 4K DDIMM VPD port 0
    ret = cli.run_command("get-dimm-seeprom 0 0 3 0") # reading DDIMM VPD port 0
    if ret != None:
        # simics object for the image
        image = simics.SIM_get_object(ret)
        # string of bytes from simics interface
        read_buf = image.iface.image.get(0, image.size) # interface takes start and length

        # Probably this file will be deleted once we write to BMC
        with open(file_name, 'ab') as f:
            f.write(read_buf)

    # now add 4K DDIMM VPD port 1
    ret = cli.run_command("get-dimm-seeprom 0 0 3 1") # reading DDIMM VPD port 1
    if ret != None:
        # simics object for the image
        image = simics.SIM_get_object(ret)
        #string of bytes from simics interface
        read_buf = image.iface.image.get(0, image.size) # interface takes start and length

        # Probably this file will be deleted once we write to BMC
        with open(file_name, 'ab') as f:
            f.write(read_buf)

    ##################################### Populate Proc 1 Records ####################################
    # now add 64K mvpd record for processor 1 (0x50001)
    ret = cli.run_command("get-seeprom 0 1 2") # reading MVPD

    if ret != None:
        # simics object for the image
        image = simics.SIM_get_object(ret)
        # string of bytes from simics interface
        read_buf = image.iface.image.get(0x30000, 0x10000) # interface takes start and length

        # Probably this file will be deleted once we write to BMC
        with open(file_name, 'ab') as f:
            f.write(read_buf)

    # now add 4K DDIMM VPD port 0
    ret = cli.run_command("get-dimm-seeprom 0 1 3 2") # reading DDIMM VPD port 0
    if ret != None:
        # simics object for the image
        image = simics.SIM_get_object(ret)
        # string of bytes from simics interface
        read_buf = image.iface.image.get(0, image.size) # interface takes start and length

        # Probably this file will be deleted once we write to BMC
        with open(file_name, 'ab') as f:
            f.write(read_buf)

    # now add 4K DDIMM VPD port 1
    ret = cli.run_command("get-dimm-seeprom 0 1 3 3") # reading DDIMM VPD port 1
    if ret != None:
        # simics object for the image
        image = simics.SIM_get_object(ret)
        #string of bytes from simics interface
        read_buf = image.iface.image.get(0, image.size) # interface takes start and length

        # Probably this file will be deleted once we write to BMC
        with open(file_name, 'ab') as f:
            f.write(read_buf)

    return None


###########################################################################
# Find what the local file name should be for generated EECACHE
# bmc_files is a parameter passed into runsim
###########################################################################
def find_eecache_file( bmc_files_str ):
    x = re.search('/host/(.+):/usr/local/share/pnor/EECACHE', bmc_files_str)
    if x != None:
      #print(x.group(1))
      return x.group(1)
    return None

##########################################################################
# Resolve the relative simics path to absolute path
# This is to support copying EECACHE to the BMC
# @param bmc_files_str - simics bmc_files string
# @param absolute_simics_eecache - result of lookup-file on eecache part
# @return Altered version of bmc_files_string where relative eecache is
#         replaced with absolute_simics_eecache
##########################################################################
def resolve_eecache_path( bmc_files_str, absolute_simics_eecache ):
    #print "resolve_eecache_path("+bmc_files_str+ ", "+absolute_simics_eecache+")"
    x = re.sub(r'([^,]+):/usr/local/share/pnor/EECACHE', absolute_simics_eecache+":/usr/local/share/pnor/EECACHE", bmc_files_str)
    if x != None:
      return x
    return None

###########################################################################
# Generate eecache (MAIN FUNCTION)
# @param eecache_file = local file to create for EECACHE
# @param version = 1 or 2 (1 = i2c only, 2 = i2c version 2, 3 = i2c + spi)
###########################################################################
def eecache_gen(eecache_file, version):
    if eecache_file != None:
        # create eecache
        #print "Create eecache: hb_eecache_setup(", eecache_file, ", ", version, ",0)"
        hb_eecache_setup(eecache_file, version, 0)
    return None

