import utils

search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"


def setup(session):
    model_url = utils.download_model('en-ner-person.bin', session)
    sent_url = utils.download_model('en-sent.bin', session)
    token_url = utils.download_model('en-token.bin', session)
    search_context = {
        "name": search_context_name,
        "matchers": [
            {
                "name": "CcnMatcher",
                "type": "pattern",
                "pattern": r"\b(4\d{12}(\d{3})?)|(5[1-5]\d{14})|(3[47]\d{13})|(3(0[0-5]|[68]\d)\d{11})|(6(011|5\d{"
                           r"2})\d{12})|((2131|1800|35\d{3})\d{11})|(8\d{15})\b "
            },
            {
                "name": "EmailMatcher",
                "type": "pattern",
                "pattern": r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,4}\b"
            },
            {
                "name": "NERMatcher",
                "type": "ner",
                "modelUrl": model_url,
                "sentenceDetectorUrl": sent_url,
                "tokenizerUrl": token_url
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
            },
            {
                "name": "FpeRule",
                "type": "cosort",
                "expression": r"enc_fp_aes256_alphanum(${INPUT})"
            }
        ],
        "ruleMatchers": [
            {
                "name": "FpeRuleMatcher",
                "type": "name",
                "rule": "FpeRule",
                "pattern": ".*"
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

    utils.create_context("searchContext", search_context, session)
    utils.create_context("maskContext", mask_context, session)
    utils.create_context("files/fileSearchContext", file_search_context, session)
    utils.create_context("files/fileMaskContext", file_mask_context, session)


def teardown(session):
    utils.destroy_context("searchContext", search_context_name, session)
    utils.destroy_context("maskContext", mask_context_name, session)
    utils.destroy_context("files/fileSearchContext", file_search_context_name, session)
    utils.destroy_context("files/fileMaskContext", file_mask_context_name, session)
