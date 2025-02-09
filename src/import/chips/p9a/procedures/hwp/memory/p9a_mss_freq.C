/* IBM_PROLOG_BEGIN_TAG                                                   */
/* This is an automatically generated prolog.                             */
/*                                                                        */
/* $Source: src/import/chips/p9a/procedures/hwp/memory/p9a_mss_freq.C $   */
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
/// @file p9a_mss_freq.C
/// @brief Calculate and save off DIMM frequencies
///
// *HWP HWP Owner: Andre Marin <aamarin@us.ibm.com>
// *HWP HWP Backup: Louis Stermole <stermole@us.ibm.com>
// *HWP Team: Memory
// *HWP Level: 2
// *HWP Consumed by: FSP:HB

// fapi2
#include <fapi2.H>

// mss lib
#include <p9a_mss_freq.H>

#include <lib/freq/axone_freq_traits.H>
#include <lib/eff_config/p9a_data_init_traits.H>
#include <lib/eff_config/explorer_attr_engine_traits.H>
#include <generic/memory/lib/data_engine/data_engine.H>
#include <generic/memory/lib/utils/find.H>
#include <generic/memory/lib/spd/spd_facade.H>
#include <generic/memory/lib/utils/count_dimm.H>
#include <generic/memory/lib/utils/freq/gen_mss_freq.H>
#include <generic/memory/mss_git_data_helper.H>
#include <lib/plug_rules/p9a_plug_rules.H>

///
/// @brief Calculate and save off DIMM frequencies
/// @param[in] i_target port target
/// @return FAPI2_RC_SUCCESS iff ok
///
fapi2::ReturnCode p9a_mss_freq( const fapi2::Target<fapi2::TARGET_TYPE_PROC_CHIP>& i_target )
{
    mss::display_git_commit_info("p9a_mss_freq");

    // If there are no DIMM, we can just get out.
    if (mss::count_dimm(mss::find_targets<fapi2::TARGET_TYPE_MEM_PORT>(i_target)) == 0)
    {
        FAPI_INF("Seeing no DIMM on %s, no freq to set", mss::c_str(i_target));
        return fapi2::FAPI2_RC_SUCCESS;
    }

    // We will first set pre-eff_config attribes
    // Note that we have to go through the MEM_PORT to get to the DIMM targets because of the
    // target hierarchy in Axone
    for(const auto& p : mss::find_targets<fapi2::TARGET_TYPE_MEM_PORT>(i_target))
    {
        for(const auto& d : mss::find_targets<fapi2::TARGET_TYPE_DIMM>(p))
        {
            std::vector<uint8_t> l_raw_spd;
            FAPI_TRY(mss::spd::get_raw_data(d, l_raw_spd));
            {
                // Gets the SPD facade
                fapi2::ReturnCode l_rc(fapi2::FAPI2_RC_SUCCESS);
                mss::spd::facade l_spd_decoder(d, l_raw_spd, l_rc);

                // Checks that the facade was setup correctly
                FAPI_TRY( l_rc, "Failed to initialize SPD facade for %s", mss::spd::c_str(d) );

                // Set pre-eff_config SPD driven attributes
                FAPI_TRY( (mss::gen::attr_engine<mss::proc_type::AXONE, mss::pre_data_init_fields>::set(l_spd_decoder)),
                          "Failed gen::attr_engine<mss::proc_type::AXONE, mss::pre_data_init_fields>::set on %s", mss::spd::c_str(d) );

                // Set pre_eff_config attributes derived from other attributes
                FAPI_TRY( (mss::gen::attr_engine<mss::proc_type::AXONE, mss::generic_metadata_fields>::set(d)),
                          "Failed gen::attr_engine<mss::proc_type::AXONE, mss::generic_metadata_fields>::set on %s", mss::spd::c_str(d) );
            }
        }

    }

    // Check plug rules.
    FAPI_TRY( mss::plug_rule::enforce_pre_freq(i_target),
              "Failed enforce_plug_rules for %s", mss::c_str(i_target) );

    // Set frequency attributes
    FAPI_TRY(mss::generate_freq<mss::proc_type::AXONE>(i_target));

fapi_try_exit:
    return fapi2::current_err;
}
