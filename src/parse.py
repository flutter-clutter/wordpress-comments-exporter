import re
import datetime
from urllib.parse import urlparse
from xml.etree import ElementTree
from xml.etree.ElementTree import iterparse

import time
import hashlib
import sys
import os


def parse_pubdate(datestr: str):
    datestr = re.sub(r' \+0000$', '', datestr)
    datestr = re.sub(r'-0001', '1970', datestr)
    return datetime.datetime.strptime(datestr, '%a, %d %b %Y %H:%M:%S')

def parse_post(post):
    out = {}
    for element in post.iter():
        if 'post_name' in element.tag:
            out['post_name'] = element.text
        elif 'pubDate' in element.tag and element.text:
            out['pubDate'] = parse_pubdate(element.text)
        elif 'link' in element.tag:
            out['link'] = element.text
    return out

def parse_comment(comment):
    out = {}
    for element in comment.iter():
        if 'comment_author_email' in element.tag:
            out['comment_author_email'] = element.text
        elif 'comment_author_IP' in element.tag:
            out['comment_author_IP'] = element.text
        elif 'comment_author_url' in element.tag:
            out['comment_author_url'] = element.text
        elif 'comment_author' in element.tag:
            out['comment_author'] = element.text
        elif 'comment_content' in element.tag:
            out['comment_content'] = element.text
        elif 'comment_date' in element.tag:
            out['comment_date'] = datetime.datetime.strptime(element.text, '%Y-%m-%d %H:%M:%S')
        elif 'comment_approved' in element.tag:
            out['comment_approved'] = bool(element.text)
    return out

def get_comments(post, post_dict: dict):
    if ('WP_URL' not in os.environ or os.environ['WP_URL'] == ''):
      print('Please provide a variable "WP_URL" in your .env file')
      sys.exit()

    comments = post.findall('{http://wordpress.org/export/1.2/}comment')

    for comment in comments:
        raw_data_dict = {}
        data_dict = {}

        for comment_attribute in comment.iter():
            raw_data_dict[comment_attribute.tag] = comment_attribute.text

        path = post_dict['link'].split(os.environ['WP_URL'] + '/')[1]
        path_parts = path.split('/')

        if len(path_parts) > 4:
            title=path_parts[2]

            post_pub_date_time = post_dict['pubDate']
            month = '0{month}'.format(month=post_pub_date_time.month) if post_pub_date_time.month < 10 else post_pub_date_time.month
            day = '0{day}'.format(day=post_pub_date_time.day) if post_pub_date_time.day < 10 else post_pub_date_time.day

            foldername = '{year}-{month}-{day}-{title}'.format(year=post_pub_date_time.year, month=month, day=day, title=path_parts[2])
            data_dict['foldername'] = foldername
        else:
            data_dict['foldername'] = post_dict['post_name']

        if '{http://wordpress.org/export/1.2/}comment_approved' not in raw_data_dict:
            continue

        if '{http://wordpress.org/export/1.2/}comment_type' not in raw_data_dict:
            continue

        comment_approved = raw_data_dict['{http://wordpress.org/export/1.2/}comment_approved'] if '{http://wordpress.org/export/1.2/}comment_approved' in raw_data_dict else None

        if comment_approved != '1' or raw_data_dict['{http://wordpress.org/export/1.2/}comment_type'] == 'pingback':
            continue

        try:
            data_dict['date'] = raw_data_dict['{http://wordpress.org/export/1.2/}comment_date_gmt']
        except:
            print('Error parsing comment date')

        pattern = '%Y-%m-%d %H:%M:%S'
        epoch = int(time.mktime(time.strptime(data_dict['date'], pattern)))
        comment_file = "comment-" + str(epoch) + ".yml"
        data_dict['filename'] = comment_file

        try:
            data_dict['_id'] = raw_data_dict['{http://wordpress.org/export/1.2/}comment_id']
        except:
            print('Error parsing comment id')
        try:
            data_dict['name'] = raw_data_dict['{http://wordpress.org/export/1.2/}comment_author']
        except:
            print('Error parsing comment name')
        try:
            if raw_data_dict['{http://wordpress.org/export/1.2/}comment_parent'] != '0':
                data_dict['reply_to'] = raw_data_dict['{http://wordpress.org/export/1.2/}comment_parent']
        except:
            print('Error parsing comment parent')
        try:
            temp_email = raw_data_dict['{http://wordpress.org/export/1.2/}comment_author_email']
            temp_email = temp_email.strip()
            temp_email = temp_email.lower()
            data_dict['email'] = temp_email
            temp_email = temp_email.encode('utf-8')
            data_dict['email_hash'] = hashlib.md5(temp_email).hexdigest()
        except Exception as e:
            print(e)
        try:
            data_dict['comment'] = raw_data_dict['{http://wordpress.org/export/1.2/}comment_content']
        except:
            print('Error parsing comment content')

        comment.clear()
        yield data_dict


class CommentParser(object):
    def __init__(self, input_file: str):
        self.input_file = input_file

    def get_items(self):
        root = ElementTree.fromstring(self.input_file)

        for channel in root:
            for post in channel:
                if post.tag != 'item':
                    continue

                out = parse_post(post)
                out['comments'] = get_comments(post, out)
                yield out
                post.clear()
