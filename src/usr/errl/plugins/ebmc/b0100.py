# IBM_PROLOG_BEGIN_TAG
# This is an automatically generated prolog.
#
# $Source: src/usr/errl/plugins/ebmc/b0100.py $
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
import json
import socket
import struct
from udparsers.helpers.symbols import hbSymbolTable
import udparsers.helpers.hwasCallout
from udparsers.helpers.errludP_Helpers import (
    hexDump, memConcat, hexConcat, intConcat, findNull, strConcat, unknownStr )

class errludP_errl:
    def ErrlUserDetailsParserString(ver, data):
        d = dict()
        i = 0
        numStrings = 1
        while i < len(data):
            indx = findNull(data, i, len(data))
            if indx == len(data):
                break
            else:
                stringData, i=strConcat(data, i, indx)
                #skip NULLs
                if(len(stringData)):
                    label = "String Data " + str(numStrings)
                    d[label]=stringData
                    numStrings += 1

        jsonStr = json.dumps(d)
        return jsonStr

    def ErrlUserDetailsParserBackTrace(ver, data):
        d = dict()

        pNfsSymFile = "/nfs/data/hbicore.syms"

        # Initialize the symbol table
        symTab = hbSymbolTable()
        readRC = symTab.readSymbols(pNfsSymFile)

        if readRC != 0:
            # Not found in NFS, look in maint for symbol file
            l_pMaintSymFile = "/maint/data/hbicore.syms"
            readRC = symTab.readSymbols( l_pMaintSymFile )
            if readRC != 0:
                # Not found in maint, look in pwd
                l_pPwdSymFile = "hbicore.syms"
                readRC = symTab.readSymbols( l_pPwdSymFile )
                if readRC != 0:
                    d["Symbols not found"]=l_pPwdSymFile
                    #symTab.nearestSymbol() will return NULL because of this.

        l_pErrlEntry = "ErrlEntry::ErrlEntry"
        l_plabel = "Backtrace"

        # loop through the buffer which is an array of 64-bit addresses
        traceEntry = []
        count = len(data) // 8
        i = 0
        for x in range(count):
            addr, i=memConcat(data, i, i+8)
            l_pSymbol = symTab.nearestSymbol(addr)
            if l_pSymbol is not None:
                if l_pErrlEntry in l_pSymbol:
                    l_pSymbol = l_pErrlEntry
                traceEntry.append("#" + str(x) + " " + addr.upper() + " " + l_pSymbol)
            else:
                traceEntry.append("#" + str(x) + " " + addr.upper())

        d[l_plabel]=traceEntry
        jsonStr = json.dumps(d)
        return jsonStr

    def ErrlUserDetailsParserLogRegister(ver, data):
        d=dict()
        i = 0
        # Values below are from AccessType enum in src/include/usr/devicefw/userif.H
        # and AccessType_DriverOnly enum in src/include/usr/devicefw/driverif.H
        # New enum values must be added to the corresponding dictionary and, if they
        # print any parameters, to the if/else statement below
        AccessType = { 0: "DeviceFW:SCOM",
                       1: "DeviceFW::PNOR - not logged",
                       2: "DeviceFW::MAILBOX - not logged",
                       3: "DeviceFW::PRESENT - not logged",
                       4: "DeviceFW::FSI",
                       5: "DeviceFW::SPD",
                       6: "DeviceFW::MVPD",
                       7: "DeviceFW::SCAN - not logged",
                       8: "DeviceFW::EEPROM",
                      10: "DeviceFW::LPC"}

        AccessType_DriverOnly = {23: "DeviceFW::XSCOM",
                                 24: "DeviceFW::I2C",
                                 25: "DeviceFW::FSISCOM",
                                 26: "DeviceFW::IBSCOM - not logged",
                                 32: "DeviceFW::SPI_EEPROM - not logged",
                                 33: "DeviceFW::SPI_TPM - not logged"}

        subDictLabel = 0
        while i < (len(data) - 4):
            subd = dict()

            if (intConcat(data, i, i+4)[0] == 0xFFFFFFFF):
                subd['LogRegister']= "Target: MASTER_PROCESSOR_CHIP_TARGET_SENTINEL"
                i += 4
            else:
                targetHUID, i=hexConcat(data, i, i+4)
                subd['LogRegister']="Target: HUID = " + targetHUID
            count = data[i]
            i += 1
            for x in range(count):
                accessValue = data[i]
                i += 1
                unknown = "Unknown " + str(accessValue) + " - not logged"
                #check for value in Access_Type dictionary
                decodeStr = AccessType.get(accessValue)
                #if not found check in AccessType_DriverOnly
                if decodeStr is None:
                    decodeStr = AccessType_DriverOnly.get(accessValue, unknown)

                subd["AccessType"]=decodeStr

                numArgs = -1
                addrParams = []
                if accessValue == 0: #DeviceFW:SCOM
                    numArgs = 1
                    addrParams.append("Scom address")
                elif accessValue == 4: #DeviceFW::FSI
                    numArgs = 1
                    addrParams.append("FSI address")
                elif accessValue == 5: #DeviceFW::SPD
                    numArgs = 1
                    addrParams.append("SPD keyword enumeration")
                elif accessValue == 6: #DeviceFW::MVPD
                    numArgs = 2
                    addrParams.append("MVPD record")
                    addrParams.append("MVPD keyword")
                elif accessValue == 8: #DeviceFW::EEPROM
                    numArgs = 2
                    addrParams.append("I2C slave device address")
                    addrParams.append("EEPROM chip number")
                elif accessValue == 10: #DeviceFW::LPC
                    numArgs = 2
                    d["Ranges"]="0=IO,1=MEM,2=FW,3=REG,4=ABS"
                    addrParams.append("Range")
                    addrParams.append("Addr")
                elif accessValue == 23: #DeviceFW::XSCOM
                    numArgs = 1
                    addrParams.append("XScom address")
                elif accessValue == 25: #DeviceFW::FSISCOM
                    numArgs = 1
                    addrParams.append("FSISCOM address")
                elif accessValue == 24: #DeviceFW::I2C
                    numArgs = 3
                    addrParams.append("I2C port")
                    addrParams.append("I2C master engine")
                    addrParams.append("Device address")

                if numArgs != -1:
                    for y in range(numArgs):
                        subd[addrParams[y]], i=hexConcat(data, i, i+8)

                    registerDataSize, i=intConcat(data, i, i+1)
                    subd['Register data']='size: ' + f'0x{registerDataSize:x}' + ' bytes'
                    subd['Hex Dump']=hexDump(data, i, i+registerDataSize)
                    i += registerDataSize

                d[str(subDictLabel)]=subd
                subDictLabel += 1


        jsonStr = json.dumps(d)
        return jsonStr

    def ErrlUserDetailsParserCallout(ver, data):
        # Data layout is defined by the callout_ud struct
        # in "src/include/usr/hwas/common/hwasCallout.H"
        # where the first section of data is always in the form:
        # 1 bytes  : type
        # 1 bytes  : flag
        # 2 bytes  : pad
        # 4 bytes  : priority

        d = dict()
        i = 0
        sizofCalloutUD = 8
        cType = data[i]

        # Keep this check in sync with callout_ud
        # in src/include/usr/hwas/common/hwasCallout.H

        # HWAS::HW_CALLOUT
        if cType == hwasCallout.calloutType.get("HW_CALLOUT"):
            # Data layout following callout_ud data
            # 4 bytes  : DeconfigEnum
            # 4 bytes  : GARD_ErrorType
            # N bytes  : Target

            # skip over callout_ud data
            i += sizofCalloutUD
            d['Callout Type']="Hardware Callout"

            deconfigState=hwasCallout.DeconfigEnum.get(intConcat(data, i, i+4)[0],
                                                        unknownStr(data, i, i+4))
            i += 4
            gardError=hwasCallout.GARD_ErrorType.get(intConcat(data, i, i+4)[0],
                                                        unknownStr(data, i, i+4))
            i += 4
            cpuID, i=hexConcat(data, i, i+4)

            # @TODO RTC:214799 - Add parsing for entity path
            #d['Target']=errludP_errl.entityPath(data, i)

            d['CPU ID']=cpuID
            d['Deconfig State']=deconfigState
            d['GARD Error Type']=gardError

        # HWAS::PROCEDURE_CALLOUT
        elif cType == hwasCallout.calloutType.get("PROCEDURE_CALLOUT"):
            # Data layout following callout_ud data
            # 4 bytes  :  epubProcedureID

            # skip over callout_ud data
            i += sizofCalloutUD
            d['Callout Type']="Procedure Callout"
            d['Procedure']=hwasCallout.epubProcedureID.get(intConcat(data, i, i+4)[0],
                                                            unknownStr(data, i, i+4))
            i += 4

        # HWAS::BUS_CALLOUT
        elif cType == hwasCallout.calloutType.get("BUS_CALLOUT"):
            # Data layout following callout_ud data
            # 4 bytes  : busTypeEnum
            # N bytes  : Target 1
            # N bytes  : Target 2

            # skip over callout_ud data
            i += sizofCalloutUD
            d['Bus Type']=hwasCallout.busTypeEnum.get(intConcat(data, i, i+4)[0],
                                                        unknownStr(data, i, i+4))
            i += 4

            # @TODO RTC:214799 - Add parsing for entity path
            #d['Target 1']=errludP_errl.entityPath(data, i)
            #d['Target 2']=errludP_errl.entityPath(data, j)

         # HWAS::CLOCK_CALLOUT
        elif cType == hwasCallout.calloutType.get("CLOCK_CALLOUT"):
            # Data layout following callout_ud data
            # 4 bytes  : clockTypeEnum
            # 4 bytes  : DeconfigEnum
            # 4 bytes  : GARD_ErrorType
            # N bytes  : Target

            # skip over callout_ud data
            i += sizofCalloutUD
            d['Clock Type']=hwasCallout.clockTypeEnum.get(intConcat(data, i, i+4)[0],
                                                                unknownStr(data, i, i+4))
            i += 4
            d['Deconfig State']=hwasCallout.DeconfigEnum.get(intConcat(data, i, i+4)[0],
                                                                unknownStr(data, i, i+4))
            i += 4
            d['GARD Error Type']=hwasCallout.GARD_ErrorType.get(intConcat(data, i, i+4)[0],
                                                                unknownStr(data, i, i+4))
            i += 4

            # @TODO RTC:214799 - Add parsing for entity path
            #d['Target']=errludP_errl.entityPath(data, i)

        # HWAS::PART_CALLOUT
        elif cType == hwasCallout.calloutType.get("PART_CALLOUT"):
            # Data layout following callout_ud data
            # 4 bytes  : partTypeEnum
            # 4 bytes  : DeconfigEnum
            # 4 bytes  : GARD_ErrorType
            # N bytes  : Target

            # skip over callout_ud data
            i += sizofCalloutUD
            d['Part Type']=hwasCallout.partTypeEnum.get(intConcat(data, i, i+4)[0],
                                                                unknownStr(data, i, i+4))
            i += 4
            d['Deconfig State']=hwasCallout.DeconfigEnum.get(intConcat(data, i, i+4)[0],
                                                                unknownStr(data, i, i+4))
            i += 4
            d['GARD Error Type']=hwasCallout.GARD_ErrorType.get(intConcat(data, i, i+4)[0],
                                                                unknownStr(data, i, i+4))
            i += 4

            # @TODO RTC:214799 - Add parsing for entity path
            #d['Target']=errludP_errl.entityPath(data, i)

        # HWAS::SENSOR_CALLOUT
        elif calloutType == hwasCallout.calloutType.get("SENSOR_CALLOUT"):
            # Data layout following callout_ud data
            # 4 bytes  : sensorId;
            # 4 bytes  : sensorTypeEnum

            # skip over callout_ud data
            i += sizofCalloutUD
            d['Callout Type']="Sensor Callout"
            d['Sensor ID'], i=hexConcat(data, i, i+4)
            d['Sensor Type']=hwasCallout.sensorTypeEnum.get(intConcat(data, i, i+4)[0],
                                                            unknownStr(data, i, i+4))
            i += 4

        # HWAS::I2C_DEVICE_CALLOUT
        elif cType == hwasCallout.calloutType.get("I2C_DEVICE_CALLOUT"):
            # Data layout following callout_ud data
            # 1 bytes  : engine
            # 1 bytes  : port
            # 1 bytes  : address
            # N bytes  : Target

            # skip over callout_ud data
            i += sizofCalloutUD
            d['Callout type']="I2C Device Callout"
            d['Engine'], i=hexConcat(data, i, i+1)
            d['Port'], i=hexConcat(data, i, i+1)
            d['Dev Address'], i=hexConcat(data, i, i+1)

            # @TODO RTC:214799 - Add parsing for entity path
            #d['Target']=errludP_errl.entityPath(data, j)

        else:
            d['Callout type']='UNKNOWN: ' + hex(cType)

        #set i to offset for priority bytes
        i = 4
        d['Priority']=hwasCallout.callOutPriority.get(intConcat(data, i, i+4)[0],
                                                        unknownStr(data, i, i+4))
        i += 4

        calloutFlag = { 0: "", # if flag = "FLAG_NONE", print nothing
                        1: "FLAG_LINK_DOWN" }

        #set i to offset for flag byte
        i = 1
        unknown = "UNKNOWN: " + hex(socket.ntohl(data[i]))
        d['Flag']=calloutFlag.get(intConcat(data, i, i+1)[0], unknown)
        i += 1

        jsonStr = json.dumps(d)
        return jsonStr

    def ErrlUserDetailsParserStringSet(ver, data):
        # The input buffer contains N sequentially packed pairs of variable
        # length, NULL terminated strings, where each string pair is also
        # sequentially packed and the sum of the lengths of all such pairs
        # exactly equals the input buffer length.  Each string pair is
        # formatted as below, beginning from either the start of the buffer or
        # the end of the previous string pair:
        #
        # Offset  Size  Description
        # =====================================================================
        # 0       Y     NULL terminated description string describing the
        #               significance of the string to follow, Y=strlen(this
        #               string) + length (1) of NULL terminator.
        # Y       Z     NULL terminated FFDC string, where Z=strlen(this
        #               string) + length (1) of NULL terminator.

        d = dict()
        i = 0
        label = ""
        while i < len(data):
            #Key
            indx=findNull(data, i, len(data))
            label, i=strConcat(data, i, indx)
            #Value
            indx=findNull(data, i, len(data))
            d[label], i=strConcat(data, i, indx)

        jsonStr = json.dumps(d)
        return jsonStr

    def ErrlUserDetailsParserBuild(ver, data):
        d=dict()
        i = 0
        sizeofImageBuild = 28

        if len(data) == sizeofImageBuild:
            d['Build Date']=f'{intConcat(data, i, i+4)[0]:08}'
            i += 4
            d['Build Time']=f'{intConcat(data, i, i+4)[0]:04}'
            i += 4
            indx = findNull(data, i, len(data))
            d['Buld Tag'], i=strConcat(data, i, indx)
        else:
            d['Build Buffer Length']=hex(len(data))
            d['Expected Length']=hex(sizeofImageBuild)
            d['Hex Dump']=hexDump(data, i, len(data))

        jsonStr = json.dumps(d)
        return jsonStr

    def ErrlUserDetailsParserSysState(ver, data):
        #***** Memory Layout *****
        # 1 bytes  : Major Istep
        # 1 bytes  : Minor Istep

        TOTAL_SIZE = 2
        d = dict()
        i = 0
        if len(data) >= TOTAL_SIZE:
            d['Current Major Istep']=data[i]
            i += 1
            d['Current Minor Istep']=data[i]
            i += 1
            if len(data) > TOTAL_SIZE:
                d['Hex Dump']=hexDump(data, i, len(data))
        else:
            d['State Buffer Length']= hex(len(data))
            d['Expected Length']= hex(TOTAL_SIZE)
            d['Hex Dump']= hexDump(data, i, len(data))

        jsonStr = json.dumps(d)
        return jsonStr

    def ErrlUserDetailsParserWofData(ver, data):
        # Format of WofData error buffer:
        # uint16_t - # of table entries (including search for table)
        # wofTableCompareData_t - Searched for this table
        # wofTableCompareData_t - last table rejected for possible match
        # ...
        # wofTableCompareData_t - 1st table rejected for possible match
        # NOTE: format must match
        #       addWofCompareDataToErrl() in plat_wof_access.C
        d = dict()
        i = 0

        sizeofTableEntries = 2
        sizeofwofTableCompareData = 6

        # From "src/import/chips/p10/procedures/hwp/lib/pstates_common.H"
        WOF_MODE = { 0: "Any", #WOF_MODE_UNKNOWN
                     1: "Normal" } #WOF_MODE_NOMINAL

        tableEntries = 0
        if len(data) >= 2:
            tableEntries, i=intConcat(data, i, i+2)
        actualTableCount = (len(data) - sizeofTableEntries) / sizeofwofTableCompareData

        if tableEntries != actualTableCount:
            d['Total Entries Calculated']=actualTableCount
            d['Total Entries Expected']=tableEntries
            #don't go over buffer length
            tableEntries = actualTableCount

        # Verify the buffer contains at least the specified number of entries
        if (len(data) - sizeofTableEntries - tableEntries * sizeofwofTableCompareData) >= 0:
            d['Total WOF Tables Compared']=tableEntries-1
            for x in range(tableEntries):
                if x == 0:
                    d['Searched for This Table']='Tried to Match This:'
                else:
                    d['Wof Table']='#' + str(x)
                d['Core Count']=data[i]
                i += 1
                d['Mode']=WOF_MODE.get(data[i], unknownStr(data, i, i+1))
                i += 1
                d['Socket Power (Watts)'], i=intConcat(data, i, i+2)
                d['Sort Power Freq (MHz)'], i=intConcat(data, i, i+2)
        else:
            subd = dict()
            subd['WOF Buffer Length']=hex(len(data))
            subd['Total Entry Count']=tableEntries
            subd['Expected Buffer Format']='uint16_t count, match this entry, unmatched entries'
            subd['Each Entry Size']=sizeofwofTableCompareData
            subd['Hex Dump']=hexDump(data, 0, len(data))
            d['Unable to parse too small buffer']=subd

        jsonStr = json.dumps(d)
        return jsonStr

    """ This function is used by ErrlUserDetailsParserCallout
    Creates entity path string, can call errlud_parse_entity_path()

    @param[in] data: memoryview object to get data from
    @param[in] index: offset to start reading data for entity path
    @returns: a string of the entity path
    """
    def entityPath(data, index):
        if data[index] == 0xF0:
            return "MASTER_PROCESSOR_CHIP_TARGET_SENTINEL"
        # @TODO RTC:214799 - Create Generated function to print entity path
        #else:
            #return errlud_parse_entity_path()

#Dictionary with parser functions for each subtype
#Values from errlUserDetailDataSubsection enum in src/include/usr/errl/errlreasoncodes.H
errlUserDetailDataSubsection = { 1: "ErrlUserDetailsParserString",
                                 2: "ErrlUserDetailsParserTarget", # generated
                                 3: "ErrlUserDetailsParserBackTrace",
                                 4: "ErrlUserDetailsParserAttribute", # generated
                                 5: "ErrlUserDetailsParserLogRegister",
                                 6: "ErrlUserDetailsParserCallout", # uses generated function
                                 9: "ErrlUserDetailsParserStringSet",
                                 10: "ErrlUserDetailsParserBuild",
                                 11: "ErrlUserDetailsParserSysState",
                                 12: "ErrlUserDetailsParserWofData" }

def parseUDToJson(subType, ver, data):
    args = (ver, data)
    return getattr(errludP_errl, errlUserDetailDataSubsection[subType])(*args)
