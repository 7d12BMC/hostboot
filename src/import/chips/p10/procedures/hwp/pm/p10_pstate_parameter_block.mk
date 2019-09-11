# IBM_PROLOG_BEGIN_TAG
# This is an automatically generated prolog.
#
# $Source: src/import/chips/p10/procedures/hwp/pm/p10_pstate_parameter_block.mk $
#
# OpenPOWER HostBoot Project
#
# Contributors Listed Below - COPYRIGHT 2019
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
PROCEDURE=p10_pstate_parameter_block
PPB_INCLUDES=$(PROJECT_ROOT)/chips/p10/procedures/hwp/pm/include/registers
PPB_INCLUDES+=$(PROJECT_ROOT)/chips/p10/common/pmlib/include
PPB_INCLUDES+=$(PROJECT_ROOT)/chips/p10/procedures/hwp/lib
PPB_INCLUDES+=$(PROJECT_ROOT)/chips/p10/procedures/hwp/pm
$(call ADD_MODULE_INCDIR,$(PROCEDURE),$(PPB_INCLUDES))
$(call BUILD_PROCEDURE)
