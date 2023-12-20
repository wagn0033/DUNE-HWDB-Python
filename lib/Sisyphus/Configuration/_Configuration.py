#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/Configuration/_Configuration.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

# This module should NOT import anything else from this project that uses
# Config or uses anything that uses Config

import os
import shutil
import json, json5
import sys
import argparse
import subprocess
import tempfile
import re
import OpenSSL
from datetime import datetime

import logging
import logging.config

# def pp(obj):
#     print(json.dumps(obj, indent=4))

from Sisyphus import version as SISYPHUS_VERSION

API_DEV = 'dbwebapi2.fnal.gov:8443/cdbdev'
API_PROD = 'dbwebapi2.fnal.gov:8443/cdb'
DEFAULT_API = API_DEV

APPLICATION_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../.."))
CONFIG_ROOT = os.path.normpath(os.path.expanduser("~/.sisyphus"))
CONFIG_BASENAME = "config.json"
LOGGING_BASENAME = "logging.json"

KW_DEFAULT_PROFILE = "default profile"
KW_PROFILES = "profiles"
KW_REST_API = "rest api"
KW_CERT_TYPE = "certificate type"
KW_CERTIFICATE = "certificate"
KW_P12 = "p12"
KW_PEM = "pem"
KW_COUNTRY = "country"
KW_NAME = "name"
KW_COUNTRY_CODE = "country code"
KW_ID = "id"
KW_LOGGING = "logging"
KW_LOGLEVEL = "loglevel"

class Config:
    def __init__(self, *, 
                    config_root=CONFIG_ROOT, 
                    logging_basename=LOGGING_BASENAME, 
                    config_basename=CONFIG_BASENAME, 
                    args=sys.argv):
        
        self.config_root = config_root
        self.config_basename = config_basename
        self.logging_basename = logging_basename
        self.config_file = os.path.join(self.config_root, self.config_basename)
        self.logging_file = os.path.join(self.config_root, self.logging_basename)
        
        self.logger = self.getLogger("Config")
        self.logger.info("[LOG INIT] logging initialized")
        self.logger.info(f"[LOG INIT] ver={SISYPHUS_VERSION}")
        self.logger.info(f"[LOG INIT] path={APPLICATION_PATH}")
        
        self._parse_args(args)
        self.load()

        self.logger = self.getLogger("Config")
        #self._load_config(filename)
        #self._populate_config()


    def getLogger(self, name="unnamed"):
        
        if not getattr(self, "_logging_initialized", False):
            self._init_logging()
        logger = logging.getLogger(name)
       
        if getattr(self, "active_profile", None) is not None:
            if self.active_profile[KW_LOGLEVEL] is not None:
                logger.setLevel(self.active_profile[KW_LOGLEVEL])
        logger.debug(f"returning logger '{name}'")
        return logger

    def _init_logging(self):
        
        # We need to create the directory the logs will be written to
        try:
            path = os.path.dirname(self.logging_file)
            os.makedirs(path, mode=0o700, exist_ok=True) 
        except Exception:
            msg = f"Could not create the log directory at {path}"
            raise RuntimeError(msg)
        
        # Read and use the data in logging_file, if it exists
        # Otherwise, use a default version
        if os.path.exists(self.logging_file):
            # open the file
            try:
                with open(self.logging_file, "r") as f:
                    raw_data = f.read()
            except Exception:
                msg = f"The log configuration file at '{self.logging_file}' could not be read."
                raise RuntimeError(msg)
            
            # parse it as JSON5
            try:
                self.logging_data = json5.loads(raw_data)
            except Exception as ex:
                raise RuntimeError(f"'{self.logging_file}' was not a valid JSON/JSON5 file --> {ex}")
        else:
            self.logging_data = self._default_log_settings()
          
        logging.config.dictConfig(self.logging_data)
        self._logging_initialized = True   
        
        
    @property 
    def log_settings(self):
        return self.logging_data #[KW_LOGGING]
    
    @property
    def rest_api(self):
        return self.active_profile[KW_REST_API]
    
    @property
    def certificate(self):
        return self.active_profile[KW_CERTIFICATE]

    @property
    def cert_type(self):
        return self.active_profile[KW_CERT_TYPE]

    @property
    def default_profile(self):
        return self.config_data[KW_DEFAULT_PROFILE]

    def _extract_cert_info(self):
        self.logger.debug("Extracting certificate information")
            
        self.cert_has_expired = None
        self.cert_expires = None
        self.cert_fullname = None
        self.cert_username = None
        self.cert_days_left = None
        
        if self.active_profile[KW_CERTIFICATE] is None:
            self.logger.debug("There is no certificate to extract data from.")
            return 
        if self.cert_type == KW_P12:       
            self.logger.debug("Unable to extract data from P12 certificate without password")
            return 

 
        with open(self.active_profile[KW_CERTIFICATE], "r") as fp:
            ce = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, fp.read())
        
        self.cert_has_expired = ce.has_expired()
        self.cert_expires = datetime.strptime(
                    ce.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%S%z').astimezone()
        
        if self.cert_has_expired:
            self.cert_days_left = 0
        else:
            current = datetime.now().astimezone()
            self.cert_days_left = (self.cert_expires - current).days
        
        comps = [(k.decode('utf-8'), v.decode('utf-8')) for k, v in ce.get_subject().get_components()]
        
        try:
            self.cert_fullname = [ v for k, v in comps if k=='CN' and not v.startswith('UID:')][0]
        except Exception:
            self.cert_fullname = None
        
        try:
            self.cert_username = [ v for k, v in comps if k=='CN' and v.startswith('UID:')][0][4:]
        except Exception:
            self.cert_username = None
    
    
        log_msg = (f"Certificate info: {self.cert_fullname} ({self.cert_username}), "
                   f"expires {self.cert_expires.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.debug(log_msg)
                         
    
    
    def reset(self):
        self.logging_data = self._default_log_settings()
        self.config_data = {}
        
    def set_active(self):
        self.config_data[KW_DEFAULT_PROFILE] = self.profile_name
    
    def remove(self, profile_name=None):
        if profile_name is None:
            profile_name = self.profile_name
            
        if profile_name in self.profiles.keys():
            self.profiles.pop(profile_name)
            self.logger.info(f"Removed profile '{profile_name}' from configuration")
        else:
            self.logger.info(f"Unable to remove profile '{profile_name}' from configuration "
                             "because it does not exist.")
            
        # if self.default_profile == profile_name:
        #     if "default" in self.profiles.keys():
        #         self.config_data[KW_DEFAULT_PROFILE] = "default"
        #     else:
        #         if len(self.profiles
        #         self.config_data[KW_DEFAULT_PROFILE] = list(self.profiles.keys())[0]
            
    def save(self):
        '''Make the current config permanent'''

        # create the config directory, if needed
        if not os.path.exists(self.config_file):
            try:
                path = os.path.dirname(self.config_file)
                os.makedirs(path, mode=0o700, exist_ok=True) 
            except Exception:
                msg = "The configuration directory does not exist and could not be created."
                raise RuntimeError(msg)

        # If we started from a p12 file and extracted a certificate, save the certificate
        if hasattr(self, 'temp_pem_file'):
            perm_filename = os.path.join(self.config_root, f"certificate_{self.profile_name}.pem")
            shutil.copyfile(self.temp_pem_file.name, perm_filename)
            self.active_profile[KW_CERTIFICATE] = perm_filename
            del self.temp_pem_file
        
        # Delete any saved certificates that don't correspond to a current profile
        pattern = re.compile('certificate_(.*)\.pem')
        files = {
                pattern.match(f).group(1): f 
                    for f in os.listdir(self.config_root) 
                    if pattern.match(f) is not None
        }
        profiles = list(self.config_data["profiles"].keys())
        for k, v in files.items():
            if k not in profiles:
                filepath = os.path.join(self.config_root, v)
                os.remove(filepath)
        
        # Save the config file
        try:
            with open(self.config_file, "w") as f:
                f.write(json.dumps(self.config_data, indent=4))
            os.chmod(self.config_file, mode=0o600)
        except Exception:
            msg = "The configuration file could not be created."
            raise RuntimeError(msg)
     
        # Save the logging config
        try:
            with open(self.logging_file, "w") as f:
                f.write(json.dumps(self.logging_data, indent=4))
            os.chmod(self.logging_file, mode=0o600)
        except Exception:
            msg = "The logging config file could not be created."
            raise RuntimeError(msg)
     
                
            
    def load(self):
        self.logger.debug("Loading config file and merging with command line args")
        self._load_config(self.config_file)
        self._populate_config()
        self._extract_cert_info()


    def _extract_pem(self, p12_file, password):
        #print(p12_file)
       
        self.temp_pem_file = tempfile.NamedTemporaryFile(
            mode='w+b', 
            buffering=- 1, 
            encoding=None, 
            newline=None, 
            suffix=".pem", 
            prefix="tmp_", 
            dir=self.config_root, 
            delete=True,
            errors=None)
        
        #print(dir(self.temp_pem_file))
        #print(self.temp_pem_file)
        
        gen_pem = subprocess.Popen(
                            [
                                "openssl",
                                "pkcs12",
                                "-in", p12_file,
                                #"-out", outfile,
                                "-nodes",
                                "-passin", f"pass:{password}",
                            ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        
        output, errors = gen_pem.communicate()
                
        if gen_pem.returncode != 0:
            raise RuntimeError(f"Unable to extract pem certificate from p12 file: "
                            f"{errors.decode('utf-8').strip()}")
        else:
            self.temp_pem_file.write(output)
            self.temp_pem_file.flush()
        
    def _populate_config(self):
        # populate the Config object using data from both the configuration file
        # and the command line arguments. Command line arguments have priority.
        #
        # Note that this doesn't actually save the configuration for future runs!
        # You must call Config.save() to make this permanent.
        
        # identify which profile we're working with
        if self.args.profile is not None:
            self.profile_name = self.args.profile
            self.logger.debug(f"profile set to '{self.profile_name}'")
            
            # if there's no default profile, make this the default.
            if self.config_data.get(KW_DEFAULT_PROFILE, None) is None:
                self.config_data[KW_DEFAULT_PROFILE] = self.profile_name
                self.logger.debug(f"default profile set to '{self.config_data[KW_DEFAULT_PROFILE]}'")
        else:
            self.profile_name = self.config_data[KW_DEFAULT_PROFILE] = \
                        self.config_data.get(KW_DEFAULT_PROFILE, "default")
            self.logger.debug(f"using profile '{self.profile_name}'")
            
        # get the profile data for the active profile            
        profiles = self.config_data[KW_PROFILES] \
                    = self.config_data.get(KW_PROFILES, {self.profile_name: {}})
        active_profile = self.active_profile \
                    = profiles[self.profile_name] \
                    = profiles.get(self.profile_name, {})
        
        # set the log level (which will be effective only AFTER config initializes, so there
        # will be some initial info or debug messages even if level is set higher)
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'default']
        if self.args.loglevel is not None:
            if self.args.loglevel not in log_levels:
                err_msg = f"Error: --loglevel must be in {log_levels}"
                self.logger.error(err_msg)
                raise ValueError(err_msg)
            else:
                if self.args.loglevel != 'default':
                    active_profile[KW_LOGLEVEL] = self.args.loglevel
                else:
                    active_profile[KW_LOGLEVEL] = None
        else:
            active_profile[KW_LOGLEVEL] = active_profile.get(KW_LOGLEVEL, None)

        # get the REST API
        self.logger.info(f"rest_api={self.args.rest_api}, dev={self.args.dev}, prod={self.args.prod}")
        if [self.args.rest_api is not None, self.args.dev, self.args.prod].count(True) > 1:
            err_msg = "Error: --rest-api, --dev, and --prod are mutually exclusive" 
            self.logger.error(err_msg)
            raise ValueError(err_msg)

        if self.args.rest_api is not None:
            active_profile[KW_REST_API] = self.args.rest_api
        elif self.args.dev:
            active_profile[KW_REST_API] = API_DEV
        elif self.args.prod:
            active_profile[KW_REST_API] = API_PROD
        else:
            active_profile[KW_REST_API] = active_profile.get(KW_REST_API, DEFAULT_API)

        self.logger.debug(f"using rest api '{active_profile[KW_REST_API]}'")
        
        # let's figure out the certificate situation...
        # 0) if --cert is provided without --cert-type, it will guess based on the
        #    extension.
        # 1) if the command line args are --cert-type p12 --cert 'xxx.p12' --password 'xxx',
        #    extract a pem from it and make it a temporary file. The config type
        #    will be "pem" instead of "p12". The temp file will only be made 
        #    permanent if the config is saved, and future runs using this config
        #    will not need a password.
        # 2) if the args are the same but with no password,
        #    use this file at its given location. The config type will be "p12".
        #    If saved, copy the file to the config directory. Future runs will require
        #    a password.  (The current run won't be able to use the REST API.)
        # 3) If the args are --cert-type pem --cert 'xxx.pem',
        #    use this file at its given location. If the config is saved, copy it to
        #    the config directory and use that from then on.
        # 4) If there is only --password 'xxx',
        #    then the config file must contain a p12. Continue as per case #1. If saved,
        #    the cert type will be pem instead of p12.
        # 5) If there are no args, use whatever was in the config file.
        #
        # * It is an error to supply a non-existent file or an incorrect password
        # * It is an error to give a password if the cert type is pem.
        # * It is an error to give a cert type without a cert (even if there's a cert in 
        # *   the config file)
        # * It is NOT an error to supply insufficient information, but you won't be able
        #     to use the REST API.
        
        # If these are provided in command line arguments, we need to do some processing
        # before throwing them into the config structure.
        if self.args.cert is not None:
            if self.args.cert_type is not None:
                if self.args.cert_type.lower() in (KW_P12, "pem"):
                    args_cert_type = self.args.cert_type.lower()
                else:
                    raise RuntimeError("Error: certificate type must be 'pem' or 'p12'")
            elif self.args.cert.lower().endswith(KW_P12):
                args_cert_type = KW_P12
            elif self.args.cert.lower().endswith(KW_PEM):
                args_cert_type = KW_PEM
            else:
                raise RuntimeError("Error: certificate type must be 'pem' or 'p12'")
            
            active_profile[KW_CERTIFICATE] = self.args.cert
            active_profile[KW_CERT_TYPE] = args_cert_type
        else:
            if self.args.cert_type is not None:
                raise RuntimeError("Error: certificate type provided, but no certificate")
            active_profile[KW_CERTIFICATE] = active_profile.get(KW_CERTIFICATE, None)
            active_profile[KW_CERT_TYPE] = active_profile.get(KW_CERT_TYPE, None)
            
        if active_profile[KW_CERT_TYPE] == KW_PEM and self.args.password is not None:
            raise RuntimeError("Error: passwords cannot be used with pem certificates")
        
        active_profile[KW_CERTIFICATE] = active_profile.get(KW_CERTIFICATE, self.args.cert)
        
        # Now the hard part. If it's a p12 with a password, we should convert to pem.
        if active_profile[KW_CERT_TYPE] == KW_P12:
            if self.args.password is not None:
                self.logger.debug("extracting PEM certificate from P12")
                self._extract_pem(active_profile[KW_CERTIFICATE], self.args.password)
                active_profile[KW_CERT_TYPE] = KW_PEM
                active_profile[KW_CERTIFICATE] = self.temp_pem_file.name
            else:
                self.logger.debug("Using P12 certificate, but no password was supplied")
        else:
            #self.logger.debug(f"{active_profile[KW_CERT_TYPE]}, {self.args.password}")
            self.logger.debug("using PEM certificate")
     
    def _load_config(self, filename):
        
        # # find the file, or create it (plus directories) if it's missing
        # if not os.path.exists(filename):
        #     try:
        #         path = os.path.dirname(filename)
        #         os.makedirs(path, mode=0o700, exist_ok=True) 
        #         
        #         with open(filename, "w") as f:
        #             f.write(json.dumps({}, indent=4))
        #             
        #         os.chmod(filename, mode=0o600)
        #             
        #     except Exception:
        #         msg = f"The configuration file at '{filename}' does not exist and could not be created."
        #         raise RuntimeError(msg)
            
        # open the file
        try:
            with open(filename, "r") as f:
                raw_data = f.read()
        except Exception:
            # msg = f"The configuration file at '{filename}' could not be read."
            # raise RuntimeError(msg)
            self.config_data = {}
            return
        
        # parse it as JSON5
        try:
            self.config_data = json5.loads(raw_data)
        except Exception as ex:
            raise RuntimeError(f"'{filename}' was not a valid JSON/JSON5 file --> {ex}")
        

    def _parse_args(self, args=None):
        self.arg_parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)        

        group = self.arg_parser.add_argument_group(
                        'Global Configuration Options',
                        'These options are available for most scripts, and are only set '
                        'for the duration of the script. If used with the '
                        'Configuration Utility, however, they will be set permanently.')

        group.add_argument('--cert-type',
                            dest='cert_type',
                            metavar='[ p12 | pem ]',
                            required=False,
                            #help='type of certificate file being used: p12 or pem')
                            help=argparse.SUPPRESS)
        group.add_argument('--cert',
                            dest='cert',
                            metavar='<filename>',
                            required=False,
                            help='user certificate for accessing REST API')
        group.add_argument('--password', 
                            dest='password',
                            metavar='<password>',
                            required=False,
                            help='password, required if using a p12 file. '
                                 '(The utility will extract a pem certificate '
                                 'and use that; the password will not be retained.')
        group.add_argument('--dev',
                            dest='dev',
                            action='store_true',
                            required=False,
                            help=f'use the DEVELOPMENT server at {API_DEV}')
        group.add_argument('--prod',
                            dest='prod',
                            action='store_true',
                            required=False,
                            help=f'use the PRODUCTION server at {API_PROD}')
        group.add_argument('--rest-api',
                            dest='rest_api',
                            metavar='<url>',
                            required=False,
                            help=f'use the REST API at <url>, ex. {DEFAULT_API}')

        '''
        self.arg_parser.add_argument('--institution-id', '--inst-id', '--inst',
                            dest='inst_id',
                            metavar='<inst-id>',
                            required=False,
                            help='set default institution id to use for new items')
        self.arg_parser.add_argument('--institution-name', '--inst-name',
                            dest='inst_name',
                            required=False,
                            metavar='<regex>',
                            help='uses <regex> to find matching institutions. if the result '
                                  'uniquely identifies an institution, use '
                                  'that one; otherwise list all matches without adding '
                                  'any institution to the configuration') 
        
        self.arg_parser.add_argument('--country-code',
                            dest='country_code',
                            metavar='<country-code>',
                            required=False,
                            help='set default 2-letter country code to use for new items')
        self.arg_parser.add_argument('--country-name',
                            dest='country_name',
                            metavar='<regex>',
                            required=False,
                            help='uses <regex> to find matching country names. if the result '
                                  'uniquely identifies a country, use '
                                  'that country; otherwise list all matches without adding '
                                  'any country to the configuration')
        '''
        
        group.add_argument('--profile',
                            dest='profile',
                            metavar='<profile-name>',
                            required=False,
                            help="if multiple profiles exist in the system, use the profile "
                                "named <profile-name>. Otherwise, use the default profile.")
        group.add_argument('--loglevel',
                            dest='loglevel',
                            metavar='<loglevel>',
                            required=False,
                            help="Only log messages at <loglevel> or higher in severity. "
                                "(DEBUG, INFO, WARNING, ERROR, CRITICAL, or 'default' to "
                                "use the default level")    

        group.add_argument('--version',
                            action='version',
                            version=f'Sisyphus {SISYPHUS_VERSION}')

        self.args, self.remaining_args = self.arg_parser.parse_known_args(args)
    
    def _default_log_settings(self):
        '''Generate the settings for the Logging module'''
        logging_data = \
        { 
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": 
            { 
                "standard": 
                { 
                    "format": "%(asctime)s [%(levelname)s] %(filename)s, line %(lineno)d: %(message)s",
                    "datefmt": "%Y-%m-%d:%H:%M:%S"
                },
                "brief":
                { 
                    "format": "%(asctime)s [%(levelname)s] %(name)s %(message)s",
                    "datefmt": "%H:%M:%S"
                }
            },
            "handlers": { 
                "stdout": { 
                    "level": "DEBUG",
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                },
                "logfile": {
                    "level": "DEBUG",
                    "formatter": "standard",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": os.path.join(self.config_root, "log.txt"),
                    "maxBytes": 0x1000000,
                    "backupCount": 3
                }
            },
            "loggers": { 
                "": 
                {
                    "handlers": ["logfile"],
                    "level": "DEBUG",
                    "propagate": False
                },
                "urllib3.connectionpool": 
                { 
                    "handlers": ["logfile"],
                    "level": "INFO",
                    "propagate": False
                },
                "__main__": 
                {
                    "handlers": ["logfile"],
                    "level": "DEBUG",
                    "propagate": False
                },
                "Sisyphus.DataModel":
                {
                    "handlers": ["logfile"],
                    "level": "DEBUG",
                    "propagate": False
                },
                "Sisyphus.Logging":
                {
                    "handlers": ["logfile"],
                    "level": "DEBUG",
                    "propagate": False
                },
                "Sisyphus.DataModel.Tools":
                {
                    "handlers": ["logfile"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }
        return logging_data
    
def run_tests():
    #test_path = os.path.join(APPLICATION_PATH, "test/Sisyphus/Config/test_Config.py")
    #print(APPLICATION_PATH)
    #print(sys.argv) 
    #os.execvp(test_path, sys.argv)
    print("Tests have been moved to a separate directory")
    
if __name__ == '__main__':
    run_tests()
else:
    config = Config()

#logger.info("exiting module")

