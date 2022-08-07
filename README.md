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
- Challenge: Trigger the hunt on the correct Velociraptor instance (We deploy one instance per case as docker container)... (Currently solved via configuration file parameter in the module config)

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

# Copyright

Copyright 2022, Stephan Mikiss under the License Lesser GNU GPL v3.0
