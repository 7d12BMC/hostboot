/* IBM_PROLOG_BEGIN_TAG                                                   */
/* This is an automatically generated prolog.                             */
/*                                                                        */
/* $Source: src/usr/isteps/istep12/call_dmi_io_run_training.C $           */
/*                                                                        */
/* OpenPOWER HostBoot Project                                             */
/*                                                                        */
/* Contributors Listed Below - COPYRIGHT 2015,2020                        */
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
#include    <stdint.h>

#include    <trace/interface.H>
#include    <initservice/taskargs.H>
#include    <initservice/isteps_trace.H>
#include    <errl/errlentry.H>
#include    <errl/errludtarget.H>
#include    <util/utilmbox_scratch.H>
#include    <util/misc.H>
#include    <isteps/hwpisteperror.H>

//  targeting support.
#include    <targeting/common/commontargeting.H>
#include    <targeting/common/utilFilter.H>

//Fapi Support
#include    <config.h>
#include    <fapi2.H>
#include    <fapi2/plat_hwp_invoker.H>

//HWP
#include    <p9_io_dmi_linktrain.H>

#ifdef CONFIG_AXONE
#include    <exp_omi_setup.H>
#include    <p9a_omi_train.H>
#include    <exp_omi_train.H>
#include    <chipids.H> // for EXPLORER ID
#endif

using   namespace   ISTEP;
using   namespace   ISTEP_ERROR;
using   namespace   ERRORLOG;
using   namespace   TARGETING;


namespace ISTEP_12
{
void* call_dmi_io_run_training (void *io_pArgs)
{
    IStepError l_StepError;
    errlHndl_t l_err = NULL;

    TRACDCOMP( ISTEPS_TRACE::g_trac_isteps_trace, "call_dmi_io_run_training entry" );

    // Starting beginning at this istep, we may be unable to scom the OCMBs
    // until the next istep is complete, except in certain cases where the
    // hardware procedure fails. Set ATTR_ATTN_POLL_PLID so ATTN knows to
    // poll the PRD_HWP_PLID before scomming the OCMBs.
    TargetHandle_t sys = nullptr;
    targetService().getTopLevelTarget(sys);
    assert(sys != nullptr);
    sys->setAttr<ATTR_ATTN_POLL_PLID>(1);

    TARGETING::TargetHandleList l_procTargetList;
    getAllChips(l_procTargetList, TYPE_PROC);

    TRACFCOMP(ISTEPS_TRACE::g_trac_isteps_trace, "call_dmi_io_run_training: %d proc chips found",
            l_procTargetList.size());

    for (const auto & l_proc_target : l_procTargetList)
    {
        TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
            "p9_io_dmi_linktrain HWP target HUID %.8x",
            TARGETING::get_huid(l_proc_target));

        //  call the HWP with each target
        fapi2::Target<fapi2::TARGET_TYPE_PROC_CHIP> l_fapi_proc_target
                (l_proc_target);

        FAPI_INVOKE_HWP(l_err, p9_io_dmi_linktrain, l_fapi_proc_target);

        //  process return code.
        if ( l_err )
        {
            TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                "ERROR 0x%.8X:  p9_io_dmi_linktrain HWP on target HUID %.8x",
                l_err->reasonCode(), TARGETING::get_huid(l_proc_target) );

            // capture the target data in the elog
            ErrlUserDetailsTarget(l_proc_target).addToLog( l_err );

            // Create IStep error log and cross reference to error that occurred
            l_StepError.addErrorDetails( l_err );

            // Commit Error
            errlCommit( l_err, ISTEP_COMP_ID );
        }
        else
        {
            TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                     "SUCCESS :  p9_io_dmi_linktrain HWP");
        }

    }

#ifdef CONFIG_AXONE

        TARGETING::TargetHandleList l_ocmbTargetList;
        getAllChips(l_ocmbTargetList, TYPE_OCMB_CHIP);

        for (const auto & l_ocmb_target : l_ocmbTargetList)
        {
            // Only run exp_omi_train on EXPLORER OCMB targets. This step
            // cannot run on GEMINI targets.
            uint32_t chipId = l_ocmb_target->getAttr< TARGETING::ATTR_CHIP_ID>();
            fapi2::Target<fapi2::TARGET_TYPE_OCMB_CHIP> l_fapi_ocmb_target( l_ocmb_target );
            if (chipId == POWER_CHIPID::EXPLORER_16)
            {
                TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                    "Start omi training on target HUID 0x%.8X",
                    TARGETING::get_huid(l_ocmb_target) );
                FAPI_INVOKE_HWP(l_err, exp_omi_train, l_fapi_ocmb_target);

                //  process return code.
                if ( l_err )
                {
                    TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                        "ERROR 0x%.8X:  exp_omi_train HWP on target HUID 0x%.08x",
                        l_err->reasonCode(), TARGETING::get_huid(l_ocmb_target) );

                    // capture the target data in the elog
                    ErrlUserDetailsTarget(l_ocmb_target).addToLog( l_err );

                    // Create IStep error log and cross reference to error that occurred
                    l_StepError.addErrorDetails( l_err );

                    // Commit Error , continue on to next OCMB
                    errlCommit( l_err, ISTEP_COMP_ID );
                }
                else
                {
                    TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                        "SUCCESS :  exp_omi_train HWP on target 0x%.08X", TARGETING::get_huid(l_ocmb_target));
                }
            }
            else
            {
                // Gemini, just skip exp_omi_train call
                TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                    "Skipping exp_omi_train HWP on because target HUID 0x%.8X, chipId 0x%.4X is a Gemini OCMB",
                    TARGETING::get_huid(l_ocmb_target), chipId );
            }
        }

        TARGETING::TargetHandleList l_omiTargetList;
        getAllChiplets(l_omiTargetList, TYPE_OMI);

        for (const auto & l_omi_target : l_omiTargetList)
        {
            TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                "p9a_omi_train HWP target HUID %.8x",
                TARGETING::get_huid(l_omi_target));

            //  call the HWP with each OMI target
            fapi2::Target<fapi2::TARGET_TYPE_OMI> l_fapi_omi_target(l_omi_target);

            FAPI_INVOKE_HWP(l_err, p9a_omi_train , l_fapi_omi_target );

            //  process return code.
            if ( l_err )
            {
                TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                    "ERROR 0x%.8X:  p9a_omi_train HWP on target HUID %.8x",
                    l_err->reasonCode(), TARGETING::get_huid(l_omi_target) );

                // capture the target data in the elog
                ErrlUserDetailsTarget(l_omi_target).addToLog( l_err );

                // Create IStep error log and cross reference to error that occurred
                l_StepError.addErrorDetails( l_err );

                // Commit Error
                errlCommit( l_err, ISTEP_COMP_ID );
            }
            else
            {
                TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                          "SUCCESS :  p9a_omi_train HWP on 0x%.08X", TARGETING::get_huid(l_omi_target));
            }
        }

#endif

    TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace, "call_dmi_io_run_training exit" );

    // end task, returning any errorlogs to IStepDisp
    return l_StepError.getErrorHandle();

}

};
