/* IBM_PROLOG_BEGIN_TAG                                                   */
/* This is an automatically generated prolog.                             */
/*                                                                        */
/* $Source: src/import/chips/p9a/procedures/hwp/memory/p9a_omi_init.H $   */
/*                                                                        */
/* OpenPOWER HostBoot Project                                             */
/*                                                                        */
/* Contributors Listed Below - COPYRIGHT 2018,2020                        */
/* [+] International Business Machines Corp.                              */
/*                                                                        */
/*                                                                        */
/* Licensed under the Apache License, Version 2.0 (the "License");        */
/* you may not use this file except in compliance with the License.       */
/* You may obtain a copy of the License at                                */
/*                                                                        */
/*     http://www.apache.org/licenses/LICENSE-2.0                         */
/*                                                                        */
/* Unless required by applicable law or agreed to in writing, software    */
/* distributed under the License is distributed on an "AS IS" BASIS,      */
/* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or        */
/* implied. See the License for the specific language governing           */
/* permissions and limitations under the License.                         */
/*                                                                        */
/* IBM_PROLOG_END_TAG                                                     */
///
/// @file p9a_omi_init.H
/// @brief Finalize the OMI
///
// *HWP HWP Owner: Benjamin Gass <bgass@us.ibm.com>
// *HWP HWP Backup: Daniel Crowell <dcrowell@us.ibm.com>
// *HWP Team:
// *HWP Level: 2
// *HWP Consumed by: HB


#ifndef _P9A_OMI_INIT_H_
#define _P9A_OMI_INIT_H_

#include <fapi2.H>

typedef fapi2::ReturnCode (*p9a_omi_init_FP_t) (const fapi2::Target<fapi2::TARGET_TYPE_MCC>&);

extern "C"
{

///
/// @brief Finalize the OMI
///
/// @param[in] i_target                 p9a channel to work on
///
/// @return fapi2:ReturnCode. FAPI2_RC_SUCCESS if success, else error code.
///
    fapi2::ReturnCode p9a_omi_init(const fapi2::Target<fapi2::TARGET_TYPE_MCC>& i_target);

} // extern "C"


#endif
