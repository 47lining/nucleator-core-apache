# Copyright 2015 47Lining LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from nucleator.cli.utils import ValidateCustomerAction
from nucleator.cli.command import Command
import argparse, os

class LimitStacksetInstanceAction(argparse.Action):
    def __call__(self,parser,namespace,values,option_string=None):
        limit_stackset = getattr(namespace,'limit_stackset', None)
        if (limit_stackset == None):
            parser.error( "limit-stackset-instance can only be used with prior specification of limit-stackset <stackset_name>")
        else:
            setattr(namespace,self.dest,values)

class Apache(Command):
    
    name = "apache"
    
    def parser_init(self, subparsers):
        """
        Initialize parsers for this command.
        """

        # add parser for apache command
        apache_parser = subparsers.add_parser('apache')
        apache_subparsers=apache_parser.add_subparsers(dest="subcommand")

        # provision subcommand
        apache_provision=apache_subparsers.add_parser('provision', help="provision a new apache")
        apache_provision.add_argument("--customer", required=True, action=ValidateCustomerAction, help="Name of customer from nucleator config")
        apache_provision.add_argument("--cage", required=True, help="Name of cage from nucleator config")
        apache_provision.add_argument("--name", required=True, help="Name of the apache instance to provision")

        # configure subcommand
        apache_configure=apache_subparsers.add_parser('configure', help="configure a new apache")
        apache_configure.add_argument("--customer", required=True, action=ValidateCustomerAction, help="Name of customer from nucleator config")
        apache_configure.add_argument("--cage", required=True, help="Name of cage from nucleator config")
        apache_configure.add_argument("--limit-stackset", required=False, help="Limit configuration to hosts associated with any instance of specified Stackset")
        apache_configure.add_argument("--limit-stackset-instance", required=False, action=LimitStacksetInstanceAction, help="Limit configuration to hosts associated with specified instance of specified Stackset.  Requires prior specification of --limit-stackset.")
        apache_configure.add_argument("--list-hosts", required=False, action='store_true', help="List entailed hosts and stop, do not configure hosts")
        apache_configure.add_argument("--restart-nat", required=False, action='store_true', help="Stop all NAT instances, then stat them again, prior to configuration")
        apache_configure.set_defaults(list_hosts=False)
        apache_configure.set_defaults(restart_nat=False)

        # delete subcommand
        apache_delete=apache_subparsers.add_parser('delete', help="delete a previously provisioned apache stackset instance")
        apache_delete.add_argument("--customer", required=True, action=ValidateCustomerAction, help="Name of customer from nucleator config")
        apache_delete.add_argument("--cage", required=True, help="Name of cage to delete")

    def provision(self, **kwargs):
        """
        Provisions a Nucleator Apache Stackset at specied cage / customer.
        """
        cli = Command.get_cli(kwargs)
        cage = kwargs.get("cage", None)
        customer = kwargs.get("customer", None)
        if cage is None or customer is None:
            raise ValueError("cage and customer must be specified")
        extra_vars={
            "cage_name": cage,
            "customer_name": customer,
            "verbosity": kwargs.get("verbosity", None),
        }

        extra_vars["apache_deleting"]=kwargs.get("apache_deleting", False)

        name = kwargs.get("name", None)
        if name is None:
            raise ValueError("name must be specified")
        extra_vars["cluster_name"] = name
        
        extra_vars["cli_stackset_name"] = "apache"
        extra_vars["cli_stackset_instance_name"] = name
        
        command_list = []
        command_list.append("account")
        command_list.append("cage")
        command_list.append("apache")

        cli.obtain_credentials(commands = command_list, cage=cage, customer=customer, verbosity=kwargs.get("verbosity", None))
        
        return cli.safe_playbook(self.get_command_playbook("apache_provision.yml"),
                                 is_static=True, # do not use dynamic inventory script, credentials may not be available
                                 **extra_vars
        )
        
    def configure(self, **kwargs):
        """
        Configure instances within a provisioned Apache, potentially including all of 
        its provisioned Stacksets.  Configure instances across all Stacksets, or 
        limit to to specified Stackset types 
        """
        cli = Command.get_cli(kwargs)
        cage = kwargs.get("cage", None)
        customer = kwargs.get("customer", None)
        restart_nat = kwargs.get("restart_nat", False)
        limit_stackset = kwargs.get("limit_stackset", None)
        limit_stackset_instance = kwargs.get("limit_stackset_instance", None)
        list_hosts = kwargs.get("list_hosts", None)
        verbosity = kwargs.get("verbosity", None)

        if cage is None or customer is None:
            raise ValueError("cage and customer must be specified")

        extra_vars={
            "cage_name": cage,
            "customer_name": customer,
            "limit_stackset": limit_stackset,
            "limit_stackset_instance": limit_stackset_instance,
            "list_hosts": list_hosts,
            "verbosity": verbosity,
            "restart_nat": restart_nat,
        }

        command_list = []
        command_list.append("account")
        command_list.append("cage")
        command_list.append("apache")

        inventory_manager_rolename = "NucleatorApacheInventoryManager"

        cli.obtain_credentials(commands = command_list, cage=cage, customer=customer, verbosity=kwargs.get("verbosity", None)) # pushes credentials into environment

        return cli.safe_playbook(
            self.get_command_playbook("apache_configure.yml"),
            inventory_manager_rolename,
            **extra_vars
        )

    def delete(self, **kwargs):
        """
        This command deletes a previously provisioned Nucleator Apache.
        """
        kwargs["apache_deleting"]=True
        return self.provision(**kwargs)
        
# Create the singleton for auto-discovery
command = Apache()
