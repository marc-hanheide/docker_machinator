import os
import sys
import argparse
from getpass import getpass
from sstash.sstash import SecureStash

class MachinatorError(Exception): pass

def store_machine(machine_name,stash_path):
    """
    Export a docker-machine from to the machines dir.
    Based on "machine-share":
    https://github.com/bhurlow/machine-share/blob/master/export.sh
    """

    home_path = os.path.expanduser('~')
    machine_path = join(home_path,'.docker','machine','machines',\
        machine_name)
    certs_path = join(home_path,'.docker','machine','certs')

    if not os.path.isdir(machine_path):
        raise MachinatorError('Machine {} does not exist. Aborting.'
                .format(machine_name))

    # Prompt user for stash password:
    password = getpass("Stash password:")
    ss = SecureStash(stash_path,password)

    ss.write_dir(['machines',machine_name,'certs'],certs_path)
    ss.write_dir(['machines',machine_name,'machine_info'],machine_path)

    # Adding domain_name, to be domain agnostic:
    # ss.write_value(['machines',machine_name,'machine_info','domain_name'],
    #         domain_name.encode('utf-8'))

    # Avoid dependence on machine by removing home dir dependant paths and
    # replacing them with a place holder:
    config_json_key = ['machines',machine_name,'machine_info','config.json']
    config_json_data = ss.read_value(config_json_key).decode('utf-8')
    config_json_data.replace(home_path,'{{HOME}}')
    ss.write_value(config_json_key,config_json_data.encode('utf-8'))


def load_machine(machine_name,stash_path):
    """
    Import a docker-machine from the machines dir.
    """
    home_path = os.path.expanduser('~')
    machine_path = join(home_path,'.docker','machine','machines',\
        machine_name)
    certs_path = join(home_path,'.docker','machine','certs')

    # Make sure that we don't already have this machine in the homedir
    # inventory:
    if os.path.isdir(machine_path):
        raise MachinatorError('Machine {} already exists. Aborting.'\
            .format(machine_name))

    # Prompt user for stash password:
    password = getpass("Stash password:")
    ss = SecureStash(stash_path,password)

    if machine_name not in ss.get_children(['machines']):
        raise MachinatorError('Machine {} does not exist in inventory. Aborting.'\
                .format(machine_name))

    ss.read_dir(['machines',machine_name,'machine_info'],machine_path)
    # Remove current set of certs if exists:
    try:
        shutil.rmtree(certs_path)
    except FileNotFoundError:
        pass
    ss.read_dir(['machines',machine_name,'certs'],certs_path)
    
    # Replace the {{HOME}} placeholder with the current machine's home dir:
    config_json_path = join(machine_path,'config.json')
    with open(config_json_path,'r') as fr:
        config_json_data = fr.read()
    config_json_data.replace('{{HOME}}',home_path)
    with open(config_json_path,'w') as fw:
        fw.write(config_json_data)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--path', type=str,
            help='Path of stash file')
    parser.add_argument('-l','--load', action='store_true',
            help='Path of stash file')
    parser.add_argument('-s','--store', action='store_true',
            help='Path of stash file')
    pass


if __name__ == '__main__':
    sys.exit(run())

