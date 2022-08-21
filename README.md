# DFIR-IRIS Module 'IOC Auto-Hunt in Velociraptor' `iris-ioc-velo-module`

`iris-ioc-velo-module` is a IRIS processor module created with https://github.com/dfir-iris/iris-skeleton-module. It parses added IOCs and starts hunts in Velociraptor across all devices.

[Velociraptor](https://github.com/Velocidex/velociraptor) is a tool for collecting host based state information using The Velociraptor Query Language (VQL) queries.
[DFIR-IRIS](https://github.com/dfir-iris/iris-web) is an Incident Response Investigation System to collect information about a case and act as documentation platform.

This module aims to automatically create a hunt (distributed query) across all systems in Velociraptor after IOCs of a supported type was added to the IOC list in DFIR-IRIS. This module will be automatically triggered after an IOC creation.

# Development

## Velociraptor API
To create a new hunt, an API call is required. However, there are a few prerequisites to that:
1. An API config must be created during Velociraptor deployment (this also creates a dedicated API user):
```
./velociraptor --config server.config.yaml config api_client --name dfir-iris-modules --role investigator,api api.config.yaml
```
2. The pip module 'pyvelociraptor' must be installed
3. Take a look at the example client script on [GitHub](https://github.com/Velocidex/pyvelociraptor/blob/master/pyvelociraptor/client_example.py)
4. The Artifact 'Generic.Forensic.LocalHashes.Glob' must be executed before the searches for hashes start.
5. The query for a MD5 hash is as follows (multiple hashes can be added with '\n' as seperator; this hunt runs for 5 hours):
```
SELECT hunt(description='A first test hunt', artifacts='Generic.Forensic.LocalHashes.Query', spec=dict(\`Generic.Forensic.LocalHashes.Query\`=dict(Hashes='Hash\n79e7ccb7d9f9acb5fcb84e408cca72eb\n')), expires=now() + 18000) FROM scope()
```
**Attention:** It might be necessary to remove the backslashes for the backtick (`). The char escape is needed to run pyvelociraptor client in the command shell.

## DFIR-IRIS Module
- Check the iris skeleton module on [GitHub](https://github.com/dfir-iris/iris-skeleton-module)
- This module will be a Processor Module acc. to the [documentation](https://docs.dfir-iris.org/development/modules/). Guidance for an processor module is avail [here](https://docs.dfir-iris.org/development/modules/quick_start/processor/#subscribing-to-a-hook)
- Hooks we should match on see [documentation](https://docs.dfir-iris.org/development/hooks/):
  - on_postload_ioc_create
  - on_postload_ioc_update
- Should be a similar module to IrisVTModule which queries VirusTotal after IOC creation on [GitHub](https://github.com/dfir-iris/iris-vt-module)
- Challenge: Trigger the hunt on the correct Velociraptor instance (We deploy one instance per case as docker container)... (Currently solved via configuration file parameter in the module config) -> Deprecated as Velociraptor now supports multi-tenancy since 0.6.6rc1. This will be included later on.

Need to resolve the following error in docker logs:

```log
app_1       | 2022-08-07 17:34:22 :: INFO :: module_handler :: call_modules_hook :: Calling module iris_ioc_velo_module asynchronously for hook on_postload_ioc_update :: None
worker_1    | [2022-08-07 17:34:22,199: INFO/MainProcess] Task app.iris_engine.module_handler.module_handler.task_hook_wrapper[ba6e1aa7-e486-498c-8afa-23a830cbe89c] received
worker_1    | [2022-08-07 17:34:22,211: INFO/ForkPoolWorker-3] Calling module iris_ioc_velo_module for hook on_postload_ioc_update
worker_1    | [2022-08-07 17:34:22,212: ERROR/ForkPoolWorker-3] Could not import root module iris_ioc_velo_module: No module named 'iris_ioc_velo_module'
worker_1    | [2022-08-07 17:34:22,212: CRITICAL/ForkPoolWorker-3] Failed to run hook on_postload_ioc_update with module iris_ioc_velo_module. Error Unable to instantiate target module
worker_1    | [2022-08-07 17:34:22,213: WARNING/ForkPoolWorker-3] Traceback (most recent call last):
worker_1    |   File "/iriswebapp/app/iris_engine/module_handler/module_handler.py", line 453, in task_hook_wrapper
worker_1    |     raise Exception('Unable to instantiate target module')
worker_1    | Exception: Unable to instantiate target module
worker_1    | [2022-08-07 17:34:22,222: INFO/ForkPoolWorker-3] Task app.iris_engine.module_handler.module_handler.task_hook_wrapper[ba6e1aa7-e486-498c-8afa-23a830cbe89c] succeeded in 0.020947525999872596s: <iris_interface.IrisInterfaceStatus.IIStatus object at 0x7f25df5b01f0>
```

Log query:
```
sudo docker-compose logs -f | grep -v iriswebapp_nginx
```

The error is generated as this module was only installed in the app container and not on the worker.. This was not specified anywhere :/
However, after installing it on the worker as well, the module gets triggered. (Still some errors - at least other errors and I can see my log output)

I migrated the run_query function into the handle_hash function so no additional function has to be called as I received several 'Error name `run` could not be resolved errors'. However, I get the following error now. I guess this is due to some (docker) IP mixup. Potentially need correct IPs or DNS resolution..
```log
app_1       | 2022-08-20 10:46:37 :: INFO :: module_handler :: call_modules_hook :: Calling module iris_ioc_velo_module asynchronously for hook on_manual_trigger_ioc :: Get velo insight
worker_1    | [2022-08-20 10:46:37,774: INFO/MainProcess] Task app.iris_engine.module_handler.module_handler.task_hook_wrapper[6486f44d-63b4-416b-b3e7-a6465c944fc7] received
worker_1    | [2022-08-20 10:46:37,786: INFO/ForkPoolWorker-3] Calling module iris_ioc_velo_module for hook on_manual_trigger_ioc
worker_1    | [2022-08-20 10:46:37,789: INFO/ForkPoolWorker-3] Using server configuration
worker_1    | [2022-08-20 10:46:37,790: INFO/ForkPoolWorker-3] Retrieved server configuration
worker_1    | [2022-08-20 10:46:37,792: INFO/ForkPoolWorker-3] Module has initiated
worker_1    | [2022-08-20 10:46:37,793: INFO/ForkPoolWorker-3] Received on_manual_trigger_ioc with data: [<Ioc 1>]
worker_1    | [2022-08-20 10:46:37,793: INFO/ForkPoolWorker-3] Using server configuration
worker_1    | [2022-08-20 10:46:37,793: INFO/ForkPoolWorker-3] Retrieved server configuration
worker_1    | [2022-08-20 10:46:37,807: INFO/ForkPoolWorker-3] [Handle_Hash]Starting Generic.Forensic.LocalHashes.Query hunt for 79e7ccb7d9f9acb5fcb84e408cca72eb
worker_1    | [2022-08-20 10:46:37,807: INFO/ForkPoolWorker-3] [Handle_Hash]Received data: <Ioc 1>
worker_1    | [2022-08-20 10:46:37,807: INFO/ForkPoolWorker-3] [Handle_Hash] run_query function will be called
worker_1    | [2022-08-20 10:46:37,807: INFO/ForkPoolWorker-3] [run_query] was entered.
worker_1    | [2022-08-20 10:46:37,807: INFO/ForkPoolWorker-3] [run_query] creds were loaded from config file.
worker_1    | [2022-08-20 10:46:37,811: CRITICAL/ForkPoolWorker-3] Failed to run hook on_manual_trigger_ioc with module iris_ioc_velo_module. Error <_MultiThreadedRendezvous of RPC that terminated with:
worker_1    |   status = StatusCode.UNAVAILABLE
worker_1    |   details = "failed to connect to all addresses"
worker_1    |   debug_error_string = "{"created":"@1660992397.810446585","description":"Failed to pick subchannel","file":"src/core/ext/filters/client_channel/client_channel.cc","file_line":3260,"referenced_errors":[{"created":"@1660992397.810445622","description":"failed to connect to all addresses","file":"src/core/lib/transport/error_utils.cc","file_line":167,"grpc_status":14}]}"
worker_1    | >
worker_1    | [2022-08-20 10:46:37,811: WARNING/ForkPoolWorker-3] Traceback (most recent call last):
worker_1    |   File "/iriswebapp/app/iris_engine/module_handler/module_handler.py", line 447, in task_hook_wrapper
worker_1    |     task_status = mod_inst.hooks_handler(hook_name, hook_ui_name, data=_obj)
worker_1    |   File "/opt/venv/lib/python3.9/site-packages/iris_ioc_velo_module/IrisVeloInterface.py", line 94, in hooks_handler
worker_1    |     status = self._handle_ioc(data=data)
worker_1    |   File "/opt/venv/lib/python3.9/site-packages/iris_ioc_velo_module/IrisVeloInterface.py", line 128, in _handle_ioc
worker_1    |     status = velo_handler.handle_hash(ioc=element)
worker_1    |   File "/opt/venv/lib/python3.9/site-packages/iris_ioc_velo_module/velo_handler/velo_handler.py", line 147, in handle_hash
worker_1    |     for response in stub.Query(request):
worker_1    |   File "/opt/venv/lib/python3.9/site-packages/grpc/_channel.py", line 426, in __next__
worker_1    |     return self._next()
worker_1    |   File "/opt/venv/lib/python3.9/site-packages/grpc/_channel.py", line 826, in _next
worker_1    |     raise self
worker_1    | grpc._channel._MultiThreadedRendezvous: <_MultiThreadedRendezvous of RPC that terminated with:
worker_1    |   status = StatusCode.UNAVAILABLE
worker_1    |   details = "failed to connect to all addresses"
worker_1    |   debug_error_string = "{"created":"@1660992397.810446585","description":"Failed to pick subchannel","file":"src/core/ext/filters/client_channel/client_channel.cc","file_line":3260,"referenced_errors":[{"created":"@1660992397.810445622","description":"failed to connect to all addresses","file":"src/core/lib/transport/error_utils.cc","file_line":167,"grpc_status":14}]}"
worker_1    | >
worker_1    | [2022-08-20 10:46:37,820: INFO/ForkPoolWorker-3] Task app.iris_engine.module_handler.module_handler.task_hook_wrapper[6486f44d-63b4-416b-b3e7-a6465c944fc7] succeeded in 0.0438004039997395s: <iris_interface.IrisInterfaceStatus.IIStatus object at 0x7f99bf610d90>
```

### How to run the module:
1. Build the wheel from the module root directory that contains the setup.py
```
python3.9 setup.py bdist_wheel
```
2. Copy the wheel to worker and app container of iris
```
sudo docker cp dist/iris_ioc_velo_module-0.1.0-py3-none-any.whl iris-web_worker_1:/iriswebapp/dependencies/
sudo docker cp dist/iris_ioc_velo_module-0.1.0-py3-none-any.whl iris-web_app_1:/iriswebapp/dependencies/
```
3. Force a reinstall of the module on the worker and app container of iris
```
sudo docker exec -it iris-web_worker_1 /bin/sh -c "pip3 install dependencies/iris_ioc_velo_module-0.1.0-py3-none-any.whl --force-reinstall"
sudo docker exec -it iris-web_app_1 /bin/sh -c "pip3 install dependencies/iris_ioc_velo_module-0.1.0-py3-none-any.whl --force-reinstall"
```
4. Restart the worker container
```
sudo docker restart iris-web_worker_1
```


# Copyright

Copyright 2022, Stephan Mikiss under the License Lesser GNU GPL v3.0
