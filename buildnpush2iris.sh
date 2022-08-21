python3.9 setup.py bdist_wheel
docker cp dist/iris_ioc_velo_module-0.1.0-py3-none-any.whl iris-web_worker_1:/iriswebapp/dependencies/
docker cp dist/iris_ioc_velo_module-0.1.0-py3-none-any.whl iris-web_app_1:/iriswebapp/dependencies/
docker exec -it iris-web_worker_1 /bin/sh -c "pip3 install dependencies/iris_ioc_velo_module-0.1.0-py3-none-any.whl --force-reinstall"
docker exec -it iris-web_app_1 /bin/sh -c "pip3 install dependencies/iris_ioc_velo_module-0.1.0-py3-none-any.whl --force-reinstall"
docker restart iris-web_worker_1