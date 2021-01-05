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
    def _download_model(name):
        logging.info(f'Checking if {name} exists')
        if not os.path.exists(name):
            logging.info(f'{name} does not exist, downloading...')
            with requests.get(f'http://opennlp.sourceforge.net/models-1.5/{name}') as r:
                with open(name, 'wb') as f:
                    f.write(r.content)
            logging.info(f'Downloaded {name}')
      
    _download_model('en-ner-person.bin')
    _download_model('en-sent.bin')
    search_context = {
      "name": search_context_name,
      "matchers": [
        {
          "name": "EmailMatcher",
          "type": "pattern",
          "pattern": r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,4}\b"
        },
        {
          "name": "PhoneMatcher",
          "type": "pattern",
          "pattern": r"\b(\+?1?([ .-]?)?)?(\(?([2-9]\d{2})\)?([ .-]?)?)([2-9]\d{2})([ .-]?)(\d{4})(?: #?[eE][xX][tT]\.? \d{2,6})?\b" 
        },
        {
          "name": "NameMatcher",
          "type": "ner",
          "modelUrl": pathlib.Path("en-ner-person.bin").absolute().as_uri(),
          "sentenceDetectorUrl": pathlib.Path("en-sent.bin").absolute().as_uri()
        }
      ]
    }

    mask_context = {
      "name": mask_context_name,
      "rules": [
        {
          "name": "HashRule",
          "type": "cosort",
          "expression": "hash_sha2($\{INPUT\})"
        },
        {
          "name": "FpeRule",
          "type": "cosort",
          "expression": "enc_fp_aes256_alphanum($\{INPUT\})"
        }
      ],
      "ruleMatchers": [
        {
          "name": "FpeRuleMatcher",
          "type": "name",
          "rule": "FpeRule",
          "pattern": "PhoneMatcher|NameMatcher"
        },
        {
          "name": "HashRuleMatcher",
          "type": "name",
          "rule": "HashRule",
          "pattern": "EmailMatcher"
        }
      ]
    }

    file_search_context = {
      "name": file_search_context_name,
      "matchers": [
        {
          "name": search_context_name,
          "type": "searchContext"
        },
        {
          "name": "NameMatcher",
          "type": "jsonPath",
          "jsonPath": "$..name"
        },
        {
          "name": "NameMatcher",
          "type": "xmlPath",
          "xmlPath": "//name"
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
        with requests.post(url, json=data) as r:
            if r.status_code >= 300:
                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")

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
