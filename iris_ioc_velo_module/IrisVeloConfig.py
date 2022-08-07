#!/usr/bin/env python3
#
#
#  IRIS velo Source Code
#  Copyright (C) 2022 - Stephan Mikiss
#  stephan.mikiss@gmail.com
#  Created by Stephan Mikiss - 2022-08-07
#
#  License Lesser GNU GPL v3.0

module_name = "IrisVelo"
module_description = ""
interface_version = 1.1
module_version = 1.0

pipeline_support = False
pipeline_info = {}


module_configuration = [
    {
        "param_name": "velo_api_config",
        "param_human_name": "velo API config file",
        "param_description": "Specify the full path to the API config file (yaml) to be used by pyvelociraptor. This must be accessible from the DFIR-IRIS container",
        "default": None,
        "mandatory": True,
        "type": "string"
    },    
    {
        "param_name": "velo_manual_hook_enabled",
        "param_human_name": "Manual triggers on IOCs",
        "param_description": "Set to True to offers possibility to manually triggers the module via the UI",
        "default": True,
        "mandatory": True,
        "type": "bool",
        "section": "Triggers"
    },
    {
        "param_name": "velo_on_create_hook_enabled",
        "param_human_name": "Triggers automatically on IOC create",
        "param_description": "Set to True to automatically start a hunt in Velociraptor each time an IOC is created",
        "default": False,
        "mandatory": True,
        "type": "bool",
        "section": "Triggers"
    },
    {
        "param_name": "velo_on_update_hook_enabled",
        "param_human_name": "Triggers automatically on IOC update",
        "param_description": "Set to True to automatically start a hunt in Velociraptor each time an IOC is updated",
        "default": False,
        "mandatory": True,
        "type": "bool",
        "section": "Triggers"
    }
    
]