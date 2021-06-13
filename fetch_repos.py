# -*- coding: utf-8 -*-
"""githubRepos.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kW5g4-0E8p-WVFPalbUFmZKGKPPzXWIm

# Base
"""

!pip install fsspec

import requests

username = 'renancleyson-dev'
secret = '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'

base_url = 'https://api.github.com'

# fetch with credentials
def get(route, **kwargs):
  return requests.get(base_url + route, auth=(username, secret), **kwargs)

import random

def get_repos():
  INITIAL_SINCE = 150000000 # since 09/2018
  since = INITIAL_SINCE
  repos = []

  while since - INITIAL_SINCE < 100000:
    r = get('/repositories', params={ 'since': since })
    repos.extend(r.json())

    link_header = r.headers['Link']
    next_link = [ link.split('; ') for link in link_header.split(',') if link.find('next') != -1]
    next_page_url = next_link[0][0][1:-1]
    since = int(next_page_url[next_page_url.rfind('?since=') + 7:])

  return repos

def get_random_repo(repositories):
  min = 0
  max = len(repositories)
  non_fork_repository = None

  while non_fork_repository == None:
    repo_i = random.randint(min, max)
    repo = repositories[repo_i]
    
    if repo['fork']:
      non_fork_repository = repo

  return non_fork_repository

# docs: https://docs.github.com/en/rest/reference/repos#list-branches
def get_branches(repo_fullname):
  r = get('/repos/' + repo_fullname + '/branches')
  return r.json()

# docs: https://docs.github.com/en/rest/reference/repos#list-repository-languages
def get_languages(repo_fullname):
  r = get('/repos/' + repo_fullname + '/languages')
  return r.json()

# docs: https://docs.github.com/en/rest/reference/repos#get-the-weekly-commit-count
def get_commits_frequency(repo_fullname):
  r = get('/repos/' + repo_fullname + '/stats/participation')
  return r.json()

def get_created_date(repo_fullname):
  r = get('/repos/' + repo_fullname)
  return r.json().get('created_at')

import json
import pandas as pd
from io import StringIO

data = []
repo_attributes = ['id', 'full_name', 'description']

repositories = get_repos()

for _ in range(700):
  random_repo = get_random_repo(repositories)
  random_repo = { attribute: random_repo[attribute] for attribute in repo_attributes }

  random_repo['branches'] = get_branches(random_repo['full_name'])
  random_repo['languages'] = get_languages(random_repo['full_name'])
  random_repo['stats'] = get_commits_frequency(random_repo['full_name'])
  random_repo['created_at'] = get_created_date(random_repo['full_name'])

  data.append(random_repo)

df = pd.read_json(StringIO(json.dumps(data)), orient='records')

df.to_csv('repositories.csv')
df.head()

df = pd.read_csv('repositories.csv')
data = df.to_dict(orient='records')

def filter_repo(repo):
  has_languages = bool(repo.get('languages')) and not repo['languages']  == '{}'
  has_branches = type(repo['branches']) == str and repo['branches'].startswith('[')
  return has_languages and has_branches

df = pd.read_json(StringIO(json.dumps(data)), orient='records')
df.to_csv('repositories.csv')
