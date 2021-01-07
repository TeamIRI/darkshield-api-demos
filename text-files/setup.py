import logging
import os
import pathlib
import requests

host = 'http://localhost:8080/api/darkshield'
search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"

def setup():
    search_context = {
        "name": search_context_name,
        "matchers": [
          {
            "name": "SsnMatcher",
            "type": "pattern",
            "pattern": r"\b(\d{3}[-]?\d{2}[-]?\d{4})\b"
          },
          {
            "name": "EmailMatcher",
            "type": "pattern",
            "pattern": r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,4}\b" 
          },
       ]
    }

    mask_context = {
        "name": mask_context_name,
        "rules": [
          {
            "name": "HashEmailRule",
            "type": "cosort",
            "expression": r"hash_sha2(${EMAIL})"
          },
          {
            "name": "RedactSsnRule",
            "type": "cosort",
            "expression": r"replace_chars(${SSN},'*',1,3,'*',5,2)"
          }
        ],
        "ruleMatchers": [
          {
            "name": "EmailRuleMatcher",
            "type": "name",
            "rule": "HashEmailRule",
            "pattern": "EmailMatcher"
          },
          {
            "name": "SsnRuleMatcher",
            "type": "name",
            "rule": "RedactSsnRule",
            "pattern": "SsnMatcher"
          }
        ]
    }

    file_search_context = {
        "name": file_search_context_name,
        "matchers": [
          {
            "name": search_context_name,
            "type": "searchContext"
          }
        ]
    }

    file_mask_context = {
        "name": file_mask_context_name,
        "rules": [
          {
            "name": mask_context_name,
            "type": "maskContext"
          }
        ]
    }

    def post(url, data):
        logging.info(f'POST: {url}')
        response = requests.post(url, json=data)
        if response.status_code >= 300:
            raise Exception(f"Failed with status {response.status_code}:\n\n{response.json()}")

    post(f"{host}/searchContext.create", search_context)
    post(f"{host}/maskContext.create", mask_context)

    post(f"{host}/files/fileSearchContext.create", file_search_context)
    post(f"{host}/files/fileMaskContext.create", file_mask_context)


def teardown():
    def post(url, name):
        logging.info(f'POST: {url}')
        requests.post(url, json={'name': name})
    
    post(f"{host}/searchContext.destroy", search_context_name)
    post(f"{host}/maskContext.destroy", mask_context_name)
    post(f"{host}/files/fileSearchContext.destroy", file_search_context_name)
    post(f"{host}/files/fileMaskContext.destroy", file_mask_context_name)
