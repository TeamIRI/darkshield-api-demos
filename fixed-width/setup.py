import utils

search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"

def setup(session):
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
            "name": "EncEmailRule",
            "type": "cosort",
            "expression": r"enc_fp_aes256_alphanum(${EMAIL})"
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
            "rule": "EncEmailRule",
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
      ],
      "configs": {
        "fixed": {
          "maxCharsPerColumn": 20,
          "maxColumns": 1,
          "columnWidths": [
            5, 13, 31, 11
          ]
        }
      }
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