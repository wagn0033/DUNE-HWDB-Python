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



def parse(command_line_args=sys.argv):
    parser = argparse.ArgumentParser(
        description='Saves authentication info in ~/.sisyphus/config.json')
    parser.add_argument('--reset',
                        dest='reset',
                        action='store_true',
                        required=False,
                        help='resets everything in the configuration '
                             '(i.e., reset the configuration, then add everything '
                             'else provided in this command line')
    parser.add_argument('--set-active',
                        dest='set_active',
                        action='store_true',
                        required=False,
                        help='set this profile to be the default') 
    args = parser.parse_known_args(command_line_args)
    return args
    
  
def show_summary(config):
    print()
    print("Configuration Summary:")
    print("======================")
    
    if config.profile_name == config.default_profile:
        default_info_msg = "(default)"
    else:
        default_info_msg = f"(default is {config.default_profile})"
    
    print(f"profile:     {config.profile_name} {default_info_msg}")
    print(f"REST API:    {config.rest_api}")
    
    if config.cert_type is None:
        print( "certificate: None, all commands will require '--cert <certificate>' to function")
    elif config.cert_type == Config.KW_P12:
        print(f"certificate: {Config.KW_P12}, all commands will require '--password <password> to function")
    else:
        print(f"certificate: {Config.KW_PEM}")
        
    if config.cert_type == Config.KW_PEM:
        print(f"cert info:   {config.cert_fullname} ({config.cert_username})")
        if config.cert_has_expired:
            print("cert status: Expired")
        else:
            print(f"cert status: Expires in {config.cert_days_left} days")
    
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

