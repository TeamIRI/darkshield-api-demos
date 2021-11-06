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
                "name": "CurrencyMatcher",
                "type": "pattern",
                "pattern": r"\$(?<number>\d{1,3})(,?\d{3})*(\.?\d{2})",
                "groups": ["number"]
            },
            {
                "name": "NameMatcher",
                "type": "ner",
                "modelUrl": model_url,
                "sentenceDetectorUrl": sent_url,
                "tokenizerUrl": token_url
            },
            {
                "name": "EmailMatcher",
                "type": "pattern",
                "pattern": r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,4}\b"
            },
            {
                "name": "PhoneMatcher",
                "type": "pattern",
                "pattern": r"(\+?1?([ .-]?)?)?(\(?([2-9]\d{2})\)?([ .-]?)?)([2-9]\d{2})([ .-]?)(\d{4})([ #eExXtT]*)(\d{2,6})?\b"
            },
            {
                "name": "SsnMatcher",
                "type": "pattern",
                "pattern": r"\b(\d{3}[-]?\d{2}[-]?\d{4})\b"
            }
        ]
    }

    mask_context = {
        "name": mask_context_name,
        "rules": [
            {
                "name": "FpeRule",
                "type": "cosort",
                "expression": r"enc_fp_aes256_alphanum(${NAME})"
            },
            {
                "name": "RedactSsnRule",
                "type": "cosort",
                "expression": r"replace_chars(${SSN},'*',1,3,'*',5,2)"
            },
            {
                "name": "HashRule",
                "type": "cosort",
                "expression": r"hash_sha2(${INPUT})"
            },
            {
                "name": "BlurIntRule",
                "type": "cosort",
                "expression": r"blur_int(${NUMBER}, 1, 100, 20)"
            },
            {
                "name": "EncryptionRule",
                "type": "cosort",
                "expression": r"enc_aes256(${ACCOUNT_NUMBER})"
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
                "name": "SsnRuleMatcher",
                "type": "name",
                "rule": "RedactSsnRule",
                "pattern": "SsnMatcher"
            },
            {
                "name": "HashRuleMatcher",
                "type": "name",
                "rule": "HashRule",
                "pattern": "EmailMatcher"
            },
            {
                "name": "BlurIntRuleMatcher",
                "type": "name",
                "rule": "BlurIntRule",
                "pattern": "CurrencyMatcher"
            },
            {
                "name": "EncryptionRuleMatcher",
                "type": "name",
                "rule": "EncryptionRule",
                "pattern": "AccountNumberMatcher"
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
                "name": "AccountNumberMatcher",
                "type": "excelCell",
                "sheetNamePattern": "buyers",
                "cellAddressPattern": r"B\d+"
            },
            {
                "name": "NameMatcher",
                "type": "excelCell",
                "sheetNamePattern": "buyers",
                "cellValuePattern": "Name"
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
