#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bin/configure.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

import sys
import argparse
import Sisyphus.Configuration as Config
import Sisyphus.RestApiV1 as ra

def parse(command_line_args=sys.argv):
    parser = argparse.ArgumentParser(
        add_help=True,
        parents=[Config.config.arg_parser],
        description='Saves authentication info in ~/.sisyphus/config.json')

    group = parser.add_argument_group(
                'Configuration Utility Options',
                'All configuration options above will be permanent, and the '
                'following additional options are available.')
        
    group.add_argument('--reset',
                        dest='reset',
                        action='store_true',
                        required=False,
                        help='resets everything in the configuration '
                             '(i.e., reset the configuration, then add everything '
                             'else provided in this command line')
    group.add_argument('--set-active',
                        dest='set_active',
                        action='store_true',
                        required=False,
                        help='set this profile to be the default') 
    args = parser.parse_known_args(command_line_args)
    return args

def check_server(config):
    # we wait until here to import because we want to process arguments and 
    # update the configuration before accessing the HWDB.
    from Sisyphus.RestApiV1 import session, whoami

    # if the config is invalid or incomplete, "session" will be None
    if session is None:
        msg = "Server check not attempted"
        config.logger.info(msg)
    else:
        try:
            resp = whoami(timeout=10)
        except ra.CertificateError as err:
            msg = "The server does not recognize the certificate"
            config.logger.error(msg)
            config.logger.info(f"The exception was: {err}")
        except Exception as err:
            msg = "Failed to contact server to validate certificate"
            config.logger.error(msg)
            config.logger.info(f"The exception was: {err}")
        else:
            user = f"{(resp['data']['full_name'])} ({resp['data']['username']})"
            msg = f"REST API 'whoami' returned {user}"
            config.logger.info(msg)
    return msg


def show_summary(config):
    print()
    print("Configuration Summary:")
    print("======================")
    
    if config.profile_name == config.default_profile:
        default_info_msg = "(default)"
    else:
        default_info_msg = f"(default is {config.default_profile})"
    
    print(f"profile:      {config.profile_name} {default_info_msg}")

    if config.rest_api == Config.API_DEV:
        rest_api_msg = "(development)"
    elif config.rest_api == Config.API_PROD:
        rest_api_msg = "(PRODUCTION)"
    else:
        rest_api_msg = "(custom)"

    print(f"REST API:     {config.rest_api} {rest_api_msg}")
    
    if config.cert_type is None:
        print( "certificate:  None, all commands will require '--cert <certificate>' to function")
    elif config.cert_type == Config.KW_P12:
        print(f"certificate:  {Config.KW_P12}, all commands will require '--password <password> to function")
    else:
        print(f"certificate:  {Config.KW_PEM}")
        
    if config.cert_type == Config.KW_PEM:
        print(f"cert info:    {config.cert_fullname} ({config.cert_username})")
        if config.cert_has_expired:
            print("cert status:  Expired")
        else:
            print(f"cert status:  Expires in {config.cert_days_left} days")
    
    #print(f"server check: {check_server(config)}")
    sys.stdout.write("server check: (please wait)")
    sys.stdout.flush()
    check_result = check_server(config)
    sys.stdout.write(f"\rserver check: {check_result}\033[K\n")


    print()
    
def main():
    
    args, unknowns = parse()
    
    if args.reset:
        Config.config.reset()
    if args.set_active:
        Config.config.set_active()
    
    Config.config.save()
    show_summary(Config.config)

if __name__ == '__main__':    
    sys.exit(main())

