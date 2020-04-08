from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from typing import List, Union, Tuple, Dict, Optional
import os, yaml

def create_settings_file():
  dir_path = os.path.dirname(os.path.realpath(__file__))
  settings_file = os.path.join(dir_path, "settings.yaml")
  if not os.path.isfile( settings_file ):
      template_file = os.path.join(dir_path, "settings_template.yaml")
      with open(template_file) as f:
          settings: Dict = yaml.load( f, Loader=yaml.FullLoader )
          settings['client_config_file'] = os.path.expanduser('~/.gauth/client_secrets.json')
          with open(settings_file,"w") as fout:
            yaml.dump( settings, fout )
  return settings_file

gauth = GoogleAuth( create_settings_file() )
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
  print('title: %s, id: %s' % (file1['title'], file1['id']))

