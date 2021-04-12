import utils
import pathlib
host = 'http://localhost:8080/api/darkshield'
search_context_name = "SearchContext"
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
            "name": "SsnMatcher",
            "type": "pattern",
            "pattern": r"\b(\d{3}[-]?\d{2}[-]?\d{4})\b"
          },
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
            "name": "FpeRule",
            "type": "cosort",
            "expression": r"enc_fp_aes256_alphanum(${NAME})"
          },
          {
            "name": "RedactSsnRule",
            "type": "cosort",
            "expression": r"replace_chars(${SSN},'*',1,3,'*',5,2)"
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

    utils.create_context("searchContext", search_context)
    utils.create_context("maskContext", mask_context)
    utils.create_context("files/fileSearchContext", file_search_context)
    utils.create_context("files/fileMaskContext", file_mask_context)


def teardown():
    utils.destroy_context("searchContext", search_context_name)
    utils.destroy_context("maskContext", mask_context_name)
    utils.destroy_context("files/fileSearchContext", file_search_context_name)
    utils.destroy_context("files/fileMaskContext", file_mask_context_name)
