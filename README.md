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




### How to install the module
#### Automatically
Run the *buildnpush2iris.sh* script. If you run docker as root, then run the script as root as well.

#### Manually
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

### Prerequisites
The config file for the Velociraptor API is needed. I suggest to mount it to the docker container in the docker-compose file. E.g. put the api.config.yaml into /tmp/velo-config/ and mount the folder in docker. Afterwards, specify the config file in the *velo API config file* parameter of DFIR-IRIS module management.
```
volumes:
      - iris-downloads:/home/iris/downloads
      - user_templates:/home/iris/user_templates
      - server_data:/home/iris/server_data
      - /tmp/velo-config:/tmp/velo-config
```

### Useful commands
1. Inspecting the logs of the module:
```
sudo docker-compose logs -f | grep -v iriswebapp_nginx
```


# Copyright

Copyright 2022, Stephan Mikiss under the License Lesser GNU GPL v3.0
