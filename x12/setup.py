import utils

search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"

def setup(session):
    model_url = utils.download_model('en-ner-person.bin',session)
    sent_url = utils.download_model('en-sent.bin',session)
    token_url = utils.download_model('en-token.bin',session)
    search_context = {
        "name": search_context_name,
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
            "name": "NameMatcher",
            "type": "column",
            "pattern": "PER*2"
          },
          {
            "name": "NameMatcher",
            "type": "column",
            "pattern": "N4*1"
          },
          {
            "name": "NameMatcher",
            "type": "column",
            "pattern": "N4*2"
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
