from src.parse import CommentParser
import os
import sys
import yaml
from os import path

input_dir = 'input'

xml_input_files = [
  f for f in os.listdir(input_dir) if path.isfile(path.join(input_dir, f)) and f.endswith('.xml')
]

def _create_comment_dir(comment: dict, folder_path: str):
  if not os.path.exists(folder_path):
      try:
          os.mkdir(folder_path)
      except Exception as e:
          print("{folder_path} could not be created".format(folder_path=folder_path))
          sys.exit()

def _create_comment_file(comment: dict, file_path: str):
  with open(file_path, "w") as f:
      yaml.dump(comment, f)

def _handle_comment(comment: dict):
  folder_path = path.join('output', comment['foldername'])
  file_path = path.join(folder_path, comment['filename'])

  del comment['foldername']
  del comment['filename']

  _create_comment_dir(comment, folder_path)
  _create_comment_file(comment, file_path)

def iterate_input_files():
  comment_count = 0
  for input_file in xml_input_files:
      with open(path.join(input_dir, input_file), 'r') as file_descriptor:
          for item in CommentParser(file_descriptor.read()).get_items():
              for comment in item['comments']:
                  _handle_comment(comment)
                  comment_count += 1
  if comment_count == 0:
      print('No comments were exported')
  else:
      print('{comment_count} comments were exported'.format(comment_count=comment_count))


if len(xml_input_files) == 0:
  print('Please put your xml input files into a directory called "input" in the root dir of this project')
iterate_input_files()