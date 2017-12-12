#!/user/bin/env python
# coding: utf-8

__author__ = 'WANG Ruochen'
__copyright__ = 'Copyright 2017, NewsDiscovery'
__credits__ = ['WANG Ruoche']

__license__ = 'GPL 3.0'
__version__ = '0.1'
__maintainer__ = 'WANG Ruochen'
__email__ = 'ruochwang@gmail.com'

import sys
import yaml
from typing import Tuple

global_setting_path = '../res/setting.yml'


def load_settings(file_path: str = global_setting_path) -> dict:
    """Return a dict that contains all setting information"""
    with open(file_path, 'r') as f:
        return yaml.load(f)


def load_news_sources() -> dict:
    """Return a dict that contains all the news source that NewsDiscovery crawled from."""
    return load_settings().get('newsSource')


def load_facebook_sources() -> dict:
    """
    The returned list's type is like:
    [{'name': 'name_of_fb1', 'id':'id_of_fb1'}, {'name': 'name_of_fb2', 'id':'id_of_fb2'}, ...]
    :return: List of facebook sources
    """
    return load_news_sources().get('facebookPage')


def load_facebook_account() -> Tuple:
    """

    :return: A dict that contains the credential of facebook app for web scraping
    """
    setting = load_settings()
    fb_id = setting.get('accountSetting').get('facebookAppId')
    fb_secret = setting.get('accountSetting').get('facebookAppSecret')
    return fb_id, fb_secret
