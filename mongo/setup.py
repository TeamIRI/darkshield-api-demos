import utils

host = 'http://localhost:8080/api/darkshield'
search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"

def setup(session):    
    model_url = utils.download_model('en-ner-person.bin',session)
    sent_url = utils.download_model('en-sent.bin',session)
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
          "modelUrl": model_url,
          "sentenceDetectorUrl": sent_url
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
          "pattern": "NameMatcher|PhoneMatcher"
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

    utils.create_context("searchContext", search_context,session)
    utils.create_context("maskContext", mask_context,session)
    utils.create_context("files/fileSearchContext", file_search_context,session)
    utils.create_context("files/fileMaskContext", file_mask_context,session)


def teardown(session):
    utils.destroy_context("searchContext", search_context_name,session)
    utils.destroy_context("maskContext", mask_context_name,session)
    utils.destroy_context("files/fileSearchContext", file_search_context_name,session)
    utils.destroy_context("files/fileMaskContext", file_mask_context_name,session)
