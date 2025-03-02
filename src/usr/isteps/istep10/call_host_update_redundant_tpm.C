/* IBM_PROLOG_BEGIN_TAG                                                   */
/* This is an automatically generated prolog.                             */
/*                                                                        */
/* $Source: src/usr/isteps/istep10/call_host_update_redundant_tpm.C $     */
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
#include <isteps/hwpisteperror.H>
#include <errl/errlentry.H>
#include <errl/errlmanager.H>
#include <isteps/istep_reasoncodes.H>
#include <initservice/initserviceif.H>

// targeting support
#include <targeting/common/target.H>
#include <targeting/common/commontargeting.H>
#include <targeting/common/utilFilter.H>
#include <errl/errludtarget.H>
#include <attributetraits.H>

#include <util/align.H>
#include <util/algorithm.H>
#include <istepHelperFuncs.H>
#include <secureboot/trustedbootif.H>
#include <secureboot/phys_presence_if.H>

namespace ISTEP_10
{

void* call_host_update_redundant_tpm (void *io_pArgs)
{
    TRACFCOMP(ISTEPS_TRACE::g_trac_isteps_trace,
                ENTER_MRK"call_host_update_redundant_tpm");

    ISTEP_ERROR::IStepError l_istepError;

#ifdef CONFIG_TPMDD
    TARGETING::Target* l_backupTpm = nullptr;

    do{
    TRUSTEDBOOT::getBackupTpm(l_backupTpm);
    if(!l_backupTpm)
    {
        TRACFCOMP(ISTEPS_TRACE::g_trac_isteps_trace,
                       "call_host_update_redundant_tpm: Backup TPM not found.");
        break;
    }

    TRUSTEDBOOT::initBackupTpm();

    } while(0);
#endif

#ifdef CONFIG_PHYS_PRES_PWR_BUTTON
    // Check to see if a Physical Presence Window should be opened,
    // and if so, open it.  This could result in the system being shutdown
    // to allow the system administrator to assert physical presence
    errlHndl_t l_err = nullptr;
    l_err = SECUREBOOT::handlePhysPresenceWindow();
    if (l_err)
    {
        TRACFCOMP( ISTEPS_TRACE::g_trac_isteps_trace,
                   "call_host_update_redundant_tpm: Error back from "
                   "SECUREBOOT::handlePhysPresence: "
                   TRACE_ERR_FMT,
                   TRACE_ERR_ARGS(l_err));
        l_istepError.addErrorDetails(l_err);
    }
#endif

    TRACFCOMP(ISTEPS_TRACE::g_trac_isteps_trace,
                EXIT_MRK"call_host_update_redundant_tpm");

    return l_istepError.getErrorHandle();
}

};
