
from __future__ import absolute_import, print_function, unicode_literals
from cryptography.fernet import Fernet
# Import python libs
import atexit
import logging
import os
import yaml
import json
import salt.client
import six
import time
from datetime import datetime,  timedelta
from contextlib import contextmanager


from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    __salt__: Any = None
    __opts__: Any = None

log = logging.getLogger(__name__)

def _decrypt_password(password_encrypted):
    
    encrypted_pwd = ""
    if not os.path.exists("/srv/pillar/sumakey.sls"):
        print("No /srv/pillar/sumakey.sls found")
        if os.environ.get('SUMAKEY') == None: 
            log.fatal("You don't have ENV SUMAKEY set. Use unencrypted pwd.")
            return str(password_encrypted)
        else:
            
            encrypted_pwd = os.environ.get('SUMAKEY')
    else:
        
        with open("/srv/pillar/sumakey.sls", 'r') as file:
            # Load the YAML data into a dictionary
            sumakey_dict = yaml.safe_load(file)
            encrypted_pwd = sumakey_dict["SUMAKEY"]

    if not encrypted_pwd == "":
        saltkey = bytes(str(encrypted_pwd), encoding='utf-8')
        fernet = Fernet(saltkey)
        encmessage = bytes(str(password_encrypted), encoding='utf-8')
        pwd = fernet.decrypt(encmessage)
    else:
        log.fatal("encrypted_pwd is empty. Use unencrypted pwd.")
        return str(password_encrypted)        
    
    return pwd.decode()

def _get_suma_configuration(suma_url=''):
    '''
    Return the configuration read from the master configuration
    file or directory
    '''
    suma_config = __opts__['suma_api'] if 'suma_api' in __opts__ else None

    if suma_config:
        try:
            for suma_server, service_config in six.iteritems(suma_config):
                username = service_config.get('username', None)
                password_encrypted = service_config.get('password', None)
                password = _decrypt_password(password_encrypted)
                protocol = service_config.get('protocol', 'http')

                if not username or not password:
                    log.error(
                        'Username or Password has not been specified in the master '
                        'configuration for %s', suma_server
                    )
                    return False

                ret = {
                    'api_url': '{0}://{1}/rpc/api'.format(protocol, suma_server),
                    'username': username,
                    'password': password,
                    'servername': suma_server
                }

                if (not suma_url) or (suma_url == suma_server):
                    return ret
        except Exception as exc:  # pylint: disable=broad-except
            log.error('Exception encountered: %s', exc)
            return False

        if suma_url:
            log.error(
                'Configuration for %s has not been specified in the master '
                'configuration', suma_url
            )
            return False

    return False

def _get_client_and_key(url, user, password, verbose=0):
    '''
    Return the client object and session key for the client
    '''
    session = {}
    session['client'] = six.moves.xmlrpc_client.Server(url, verbose=verbose, use_datetime=True)
    session['key'] = session['client'].auth.login(user, password)

    return session


def _get_session(server):
    '''
    Get session and key - creates a new session each time since we logout at the end of each cycle
    '''
    config = _get_suma_configuration(server)
    if not config:
        raise Exception('No config for \'{0}\' found on master'.format(server))

    session = _get_client_and_key(config['api_url'], config['username'], config['password'])
    
    client = session['client']
    key = session['key']
    
    return client, key

def _listSystems(client, key):
    '''
    List all systems with retry logic for network errors
    '''
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries + 1):
        try:
            system_list = client.system.listSystems(key, 1000010578)
            if attempt > 0:
                log.info('Successfully retrieved systems after %d retry attempts', attempt)
            return system_list
        except (six.moves.urllib.error.URLError, OSError, six.moves.http_client.HTTPException) as exc:
            if attempt < max_retries:
                log.warning('Network error on attempt %d/%d while listing systems, retrying in %d seconds: %s', 
                           attempt + 1, max_retries + 1, retry_delay, exc)
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                log.error('Failed to list systems after %d attempts due to network error: %s', max_retries + 1, exc)
                return []
        except Exception as exc:
            log.error('Exception while listing systems: %s', exc)
            return []
    
    return []

def _listSystemGroups(client, key):
    '''
    List all system groups with retry logic for network errors
    '''
    max_retries = 3
    retry_delay = 1  # Start with 1 second delay
    
    for attempt in range(max_retries + 1):
        try:
            system_group_list = client.systemgroup.listAllGroups(key)
            if attempt > 0:
                log.info('Successfully retrieved system groups after %d retry attempts', attempt)
            return system_group_list
        except (six.moves.urllib.error.URLError, OSError, six.moves.http_client.HTTPException) as exc:
            # Network/SSL related errors - these are worth retrying
            if attempt < max_retries:
                log.warning('Network error on attempt %d/%d while _listSystemGroups, retrying in %d seconds: %s', 
                           attempt + 1, max_retries + 1, retry_delay, exc)
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                log.error('Failed to list system groups after %d attempts due to network error: %s', max_retries + 1, exc)
                return []
        except six.moves.xmlrpc_client.Fault as exc:
            # XMLRpc faults (like authentication errors) - don't retry these
            log.error('XMLRpc fault while listing system groups: %s', exc)
            return []
        except Exception as exc:
            # Other unexpected errors - don't retry
            log.error('Unexpected exception while listing system groups: %s', exc)
            return []
    
    return []

def _get_system_groups(client, key):
    '''
    Get pillar info for a system
    '''
    group_info = {}
    group_info["suma_groups"] = {}
    all_groups = _listSystemGroups(client, key)
    for group in all_groups:
        #log.info("---Group info---: \n%s", group)
        if group["name"] != "":
            group_info["suma_groups"][group["name"]] = []
            try:
                # Add retry logic for listing systems in group
                max_retries = 2
                retry_delay = 1
                
                for attempt in range(max_retries + 1):
                    try:
                        systems_in_group = client.systemgroup.listSystemsMinimal(key, group["name"])
                        for system in systems_in_group:
                            group_info["suma_groups"][group["name"]].append(system["name"])
                        break  # Success, exit retry loop
                    except (six.moves.urllib.error.URLError, OSError, six.moves.http_client.HTTPException) as net_exc:
                        if attempt < max_retries:
                            log.warning('Network error on attempt %d/%d while _get_system_groups %s, retrying in %d seconds: %s', 
                                       attempt + 1, max_retries + 1, group["name"], retry_delay, net_exc)
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                        else:
                            log.error('Failed to list systems in group %s after %d attempts due to network error: %s', 
                                     group["name"], max_retries + 1, net_exc)
                            break
                    except Exception as other_exc:
                        log.error('Exception encountered while listing systems in group %s: %s', group["name"], other_exc)
                        break
            except Exception as exc:
                log.error('Unexpected error while processing group %s: %s', group["name"], exc)
    #log.info("---group_info---: \n%s", group_info)
    return group_info

def _logout_session(client, key):
    '''
    Logout session
    '''
    try:
        client.auth.logout(key)
        log.debug('Successfully logged out session with key: %s', key)
    except six.moves.xmlrpc_client.Fault as exc:
        log.warning('Failed to logout session with key %s: %s', key, exc)
    except Exception as exc:
        log.error('Unexpected error during logout for key %s: %s', key, exc)

def start(interval=20):

    log.info("Starting GetSuma engine...")
    
    # Initialize session once at startup
    suma_config = _get_suma_configuration()
    server = suma_config["servername"]
    client, key = _get_session(server)
    log.info("GetSuma engine started successfully with session key: %s", key)

    try:
        while True:
            log.info("------------------Update Suma groups as pillar------------------")
            try:
                group_info = _get_system_groups(client, key)
                log.info("GetSuma engine finished updating Suma groups.")

                #dump the group_info to a yaml file to /srv/pillar/suma_groups.sls
                # only write if group_info is not empty to avoid overwriting with empty data in case of errors
                if group_info["suma_groups"]:
                    with open("/srv/pillar/suma_groups.sls", 'w') as file:
                        yaml.dump(group_info, file)
                    
            except six.moves.xmlrpc_client.Fault as exc:
                if 'session' in str(exc).lower() or 'login' in str(exc).lower():
                    log.warning("Session expired, creating new session: %s", exc)
                    # Session expired, create new one
                    client, key = _get_session(server)
                    log.info("New session created with key: %s", key)
                    # Retry the operation
                    group_info = _get_system_groups(client, key)
                    log.info("GetSuma engine finished updating Suma groups after session refresh.")
                else:
                    log.error("XMLRpc error during operation: %s", exc)
                    raise
            except Exception as exc:
                log.error("Unexpected error during group update: %s", exc)
                # Don't raise here to keep the engine running
                
            time.sleep(interval)
            
    except KeyboardInterrupt:
        log.info("GetSuma engine interrupted, shutting down...")
    except Exception as exc:
        log.error("GetSuma engine encountered fatal error: %s", exc)
    finally:
        # Clean up session on engine shutdown
        log.info("Logging out session...")
        _logout_session(client, key)
