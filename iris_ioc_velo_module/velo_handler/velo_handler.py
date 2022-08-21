#!/usr/bin/env python3
#
#
#  IRIS velo Source Code
#  Copyright (C) 2022 - Stephan Mikiss
#  stephan.mikiss@gmail.com
#  Created by Stephan Mikiss - 2022-08-07
#
#  License Lesser GNU GPL v3.0


import traceback
from jinja2 import Template

import iris_interface.IrisInterfaceStatus as InterfaceStatus
from app.datamgmt.manage.manage_attribute_db import add_tab_attribute_field

import argparse
import json
import grpc
import time
import yaml

import pyvelociraptor
from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc

class VeloHandler(object):
    def __init__(self, mod_config, logger):
        self.mod_config = mod_config
        self.log = logger
        self.config = pyvelociraptor.LoadConfigFile(self.mod_config.get('velo_api_config'))

    def run_query(self, query, query_name):
        # Fill in the SSL params from the api_client config file. You can get such a file:
        # velociraptor --config server.config.yaml config api_client > api_client.conf.yaml
        self.log.info('[run_query func] was entered.')

        creds = grpc.ssl_channel_credentials(
            root_certificates=self.config["ca_certificate"].encode("utf8"),
            private_key=self.config["client_private_key"].encode("utf8"),
            certificate_chain=self.config["client_cert"].encode("utf8"))

        self.log.info('[run_query func] creds were loaded from config file.')

        # This option is required to connect to the grpc server by IP - we
        # use self signed certs.
        options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)

        # The first step is to open a gRPC channel to the server..
        with grpc.secure_channel(self.config["api_connection_string"],
                                creds, options) as channel:
            stub = api_pb2_grpc.APIStub(channel)

            # The request consists of one or more VQL queries. Note that
            # you can collect artifacts by simply naming them using the
            # "Artifact" plugin.
            request = api_pb2.VQLCollectorArgs(
                max_wait=1,
                max_row=100,
                Query=[api_pb2.VQLRequest(
                    Name=query_name,
                    VQL=query,
                )]
            )

            # This will block as responses are streamed from the
            # server. If the query is an event query we will run this loop
            # forever.
            for response in stub.Query(request):
                if response.Response:
                    # Each response represents a list of rows. The columns
                    # are provided in their own field as an array, to
                    # ensure column order is preserved if required. If you
                    # dont care about column order just ignore the Columns
                    # field. Note that although JSON does not specify the
                    # order of keys in a dict Velociraptor always
                    # maintains this order so an alternative to the
                    # Columns field is to use a JSON parser that preserves
                    # field ordering.

                    # print("Columns %s:" % response.Columns)

                    # The actual payload is a list of dicts. Each dict has
                    # column names as keys and arbitrary (possibly nested)
                    # values.
                    package = json.loads(response.Response)
                    self.log.info(f"[run(query)]JSON Response: {package}")

                elif response.log:
                    # Query execution logs are sent in their own messages.
                    self.log.info("%s: %s" % (time.ctime(response.timestamp / 1000000), response.log))

    def handle_hash(self, ioc):
        """
        Handles an IOC of type md5 and starts an IOC hunt in Velociraptor

        :param ioc: IOC instance
        :return: IIStatus
        """

        self.log.info(f'[Handle_Hash]Starting Generic.Forensic.LocalHashes.Query hunt for {ioc.ioc_value}')
        self.log.info(f'[Handle_Hash]Received data: {ioc}')

        query_name = f"IRIS-IOC-MD5-{ioc.ioc_value}"
        query = f"SELECT hunt(description='{query_name}', artifacts='Generic.Forensic.LocalHashes.Query', spec=dict(`Generic.Forensic.LocalHashes.Query`=dict(Hashes='Hash\n{ioc.ioc_value}\n')), expires=now() + 18000, cpu_limit=50) FROM scope()"

        self.run_query(query, query_name)

        return InterfaceStatus.I2Success()
