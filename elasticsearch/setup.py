import utils
import json
import os

absolute_path = os.path.dirname(__file__)
file_name = "credentials.json"
full_path = os.path.join(absolute_path, file_name )

search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"
nosql_search_context_name = "NoSqlSearchContext"
nosql_mask_context_name = "NoSqlMaskContext"

f = open(full_path, 'r')
json_creds = json.loads(f.read())
f.close()

SRC_URL = json_creds["src"]["url"]
SRC_DATABASE_NAME = json_creds["src"]["databaseName"]
SRC_COLLECTION_NAME = json_creds["src"]["collectionName"]
SRC_PORT = json_creds["src"]["port"]
SRC_NOSQL_TYPE = json_creds["src"]["type"]

TRGT_URL = json_creds["trgt"]["url"]
TRGT_DATABASE_NAME = json_creds["trgt"]["databaseName"]
TRGT_COLLECTION_NAME = json_creds["trgt"]["collectionName"]
TRGT_PORT = json_creds["trgt"]["port"]
TRGT_NOSQL_TYPE = json_creds["trgt"]["type"]

def setup(session):
    model_url = utils.download_model('en-ner-person.bin', session)
    sent_url = utils.download_model('en-sent.bin', session)
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

    nosql_search_context = {
        "name": nosql_search_context_name,
        "fileSearchContextName": file_search_context_name,
        "configs": {
            "url": SRC_URL,
            "databaseName": SRC_DATABASE_NAME,
            "collectionName": SRC_COLLECTION_NAME,
            "port": SRC_PORT,
            "type": SRC_NOSQL_TYPE
        }
    }

    nosql_mask_context = {
        "name": nosql_mask_context_name,
        "fileMaskContextName": file_mask_context_name,
        "configs": {
            "url": TRGT_URL,
            "databaseName": TRGT_DATABASE_NAME,
            "collectionName": TRGT_COLLECTION_NAME,
            "port": TRGT_PORT,
            "type": TRGT_NOSQL_TYPE
        }
    }
    utils.create_context("searchContext", search_context, session)
    utils.create_context("maskContext", mask_context, session)
    utils.create_context("files/fileSearchContext", file_search_context, session)
    utils.create_context("files/fileMaskContext", file_mask_context, session)
    utils.create_context("nosql/nosqlSearchContext", nosql_search_context, session)
    utils.create_context("nosql/nosqlMaskContext", nosql_mask_context, session)


def teardown(session):
    utils.destroy_context("searchContext", search_context_name, session)
    utils.destroy_context("maskContext", mask_context_name, session)
    utils.destroy_context("files/fileSearchContext", file_search_context_name, session)
    utils.destroy_context("files/fileMaskContext", file_mask_context_name, session)
    utils.destroy_context("nosql/nosqlSearchContext", nosql_search_context_name, session)
    utils.destroy_context("nosql/nosqlMaskContext", nosql_mask_context_name, session)
