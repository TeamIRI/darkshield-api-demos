import utils

search_context_name = "SearchContext"
search_context_ner_name = 'SearchNerContext'

mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"

def setup():   
    model_url = utils.download_model('en-ner-person.bin')
    sent_url = utils.download_model('en-sent.bin')
    token_url = utils.download_model('en-token.bin')
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
          "modelUrl": model_url,
          "sentenceDetectorUrl": sent_url,
          "tokenizerUrl": token_url
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
              "columns": [
                {
                  "ignoreHeader": True,
                  "pattern": "comment"
                }
              ]
            }
          },
          {
            "name": "NameMatcher",
            "type": "column",
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

    utils.create_context("searchContext", search_context)
    utils.create_context("searchContext", search_context_ner)
    utils.create_context("maskContext", mask_context)
    utils.create_context("files/fileSearchContext", file_search_context)
    utils.create_context("files/fileMaskContext", file_mask_context)


def teardown():
    utils.destroy_context("searchContext", search_context_name)
    utils.destroy_context("searchContext", search_context_ner_name)
    utils.destroy_context("maskContext", mask_context_name)
    utils.destroy_context("files/fileSearchContext", file_search_context_name)
    utils.destroy_context("files/fileMaskContext", file_mask_context_name)
