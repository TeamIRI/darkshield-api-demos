import logging
import os
import pathlib
import requests

host = 'http://localhost:8080/api/darkshield'
search_context_name = "SearchContext"
search_context_ner_name = 'SearchNerContext'

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
    _download_model('en-token.bin')
    search_context = {
        "name": search_context_name,
        "matchers": [
          {
            "name": "EmailMatcher",
            "type": "pattern",
            "pattern": r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,4}\b" 
          },
       ]
    }
    
    search_context_ner = {
      "name": search_context_ner_name,
      "matchers": [
        {
          "name": "NameMatcher",
          "type": "ner",
          "modelUrl": pathlib.Path("en-ner-person.bin").absolute().as_uri(),
          "sentenceDetectorUrl": pathlib.Path("en-sent.bin").absolute().as_uri(),
          "tokenizerUrl": pathlib.Path("en-token.bin").absolute().as_uri()
        }
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
            "name": "FpeNameRule",
            "type": "cosort",
            "expression": r"enc_fp_aes256_alphanum(${NAME},'passphrase')"
          }
        ],
        "ruleMatchers": [
          {
            "name": "HashRuleMatcher",
            "type": "name",
            "rule": "HashEmailRule",
            "pattern": "EmailMatcher"
          },
          {
            "name": "NameRuleMatcher",
            "type": "name",
            "rule": "FpeNameRule",
            "pattern": "NameMatcher"
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
            "name": search_context_ner_name,
            "type": "searchContext",
            "contentFilters": {
              "tableColumns": [
                {
                  "ignoreHeader": True,
                  "pattern": "comment"
                }
              ]
            }
          },
          {
            "name": "NameMatcher",
            "type": "tableColumn",
            "ignoreHeader": True,
            "pattern": ".*name"
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
    post(f"{host}/searchContext.create", search_context_ner)
    post(f"{host}/maskContext.create", mask_context)

    post(f"{host}/files/fileSearchContext.create", file_search_context)
    post(f"{host}/files/fileMaskContext.create", file_mask_context)


def teardown():
    def post(url, name):
        logging.info(f'POST: {url}')
        requests.post(url, json={'name': name})
    
    post(f"{host}/searchContext.destroy", search_context_name)
    post(f"{host}/searchContext.destroy", search_context_ner_name)
    post(f"{host}/maskContext.destroy", mask_context_name)
    post(f"{host}/files/fileSearchContext.destroy", file_search_context_name)
    post(f"{host}/files/fileMaskContext.destroy", file_mask_context_name)
