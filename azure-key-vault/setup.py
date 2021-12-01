import os
import pathlib

from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

import utils

search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_search_context_2_name = "FileSearchContext2"
file_mask_context_name = "FileMaskContext"
decrypt_mask_context_name = "decryptMaskContext"
decrypt_file_mask_context_name = "decryptFileMaskContext"


def getSecret(keyVaultName, secretName, args):
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    # credential = InteractiveBrowserCredential()
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    retrieved_secret = client.get_secret(secretName, version=args.version)
    return retrieved_secret.value


def setup(session, args):
    model_url = utils.download_model('en-ner-person.bin', session)
    sent_url = utils.download_model('en-sent.bin', session)
    token_url = utils.download_model('en-token.bin', session)
    keyVaultName = os.environ["KEY_VAULT_NAME"]
    secretName = os.environ["SECRET_NAME"]
    search_context = {
        "name": search_context_name,
        "matchers": [
            {
                "name": "CcnMatcher",
                "type": "pattern",
                "pattern": r"\b(4\d{12}(\d{3})?)|(5[1-5]\d{14})|(3[47]\d{13})|(3(0[0-5]|[68]\d)\d{11})|(6(011|5\d{2})\d{12})|((2131|1800|35\d{3})\d{11})|(8\d{15})\b",
                "validatorUrl": pathlib.Path('validate-credit-card.js').absolute().as_uri()
            },
            {
                "name": "DateMatcher",
                "type": "pattern",
                "pattern": r"\b([0]\d|[1][012])[-/.]?([012]\d|[3][01])[-/.]?(\d{4})\b"
            },
            {
                "name": "EmailMatcher",
                "type": "pattern",
                "pattern": r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,4}\b"
            },
            {
                "name": "IpAddressMatcher",
                "type": "pattern",
                "pattern": r"\b((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
            },
            {
                "name": "NameMatcher",
                "type": "ner",
                "modelUrl": model_url,
                "sentenceDetectorUrl": sent_url,
                "tokenizerUrl": token_url
            },
            {
                "name": "PhoneMatcher",
                "type": "pattern",
                "pattern": r"\b(\+?1?([ .-]?)?)?(\(?([2-9]\d{2})\)?([ .-]?)?)([2-9]\d{2})([ .-]?)(\d{4})(?: #?[eE][xX][tT]\.? \d{2,6})?\b"
            },
            {
                "name": "SsnMatcher",
                "type": "pattern",
                "pattern": r"\b(\d{3}[-]?\d{2}[-]?\d{4})\b"
            },
            {
                "name": "URLMatcher",
                "type": "pattern",
                "pattern": r"\b(\w+):\/\/([\w\.-@]+)\.([A-Za-z\.]{2,6})([\/\w \(\)\.-]*)*\/?\b"
            },
            {
                "name": "USZipMatcher",
                "type": "pattern",
                "pattern": r"\b\d{5}(?:-\d{4})?\b"
            },
            {
                "name": "VINMatcher",
                "type": "pattern",
                "pattern": r"\b([A-HJ-NPR-Z\d]{3})([A-HJ-NPR-Z\d]{5})([\dX])(([A-HJ-NPR-Z\d])([A-HJ-NPR-Z\d])([A-HJ-NPR-Z\d]{6}))\b",
                "validatorUrl": pathlib.Path('validate-vin-us.js').absolute().as_uri()
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
                "expression": "enc_fp_aes256_alphanum(${{INPUT}}, \"{}\")".format(getSecret(keyVaultName, secretName, args))
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
    decrypt_mask_context = {
        "name": decrypt_mask_context_name,
        "rules": [
            {
                "name": "DecryptionRule",
                "type": "cosort",
                "expression": "dec_fp_aes256_alphanum(${{INPUT}}, \"{}\")".format(getSecret(keyVaultName, secretName, args))
            }
        ],
        "ruleMatchers": [
            {
                "name": "DecryptionRuleMatcher",
                "type": "name",
                "rule": "DecryptionRule",
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
    file_search_context_2 = {
        "name": file_search_context_2_name,
        "matchers": [
            {
                "name": "FirstNameMatcher",
                "type": "jsonPath",
                "jsonPath": "$..firstName"
            },
            {
                "name": "LastNameMatcher",
                "type": "jsonPath",
                "jsonPath": "$..lastName"
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
        ],
        "configs": {
            "json": {
                "prettyPrint": True
            }
        }
    }
    
    decrypt_file_mask_context = {
        "name": decrypt_file_mask_context_name,
        "rules": [
            {
                "name": decrypt_mask_context_name,
                "type": "maskContext"
            }
        ],
        "configs": {
            "json": {
                "prettyPrint": True
            }
        }
    }

    utils.create_context("searchContext", search_context, session)
    utils.create_context("maskContext", mask_context, session)
    utils.create_context("maskContext", decrypt_mask_context, session)
    utils.create_context("files/fileSearchContext", file_search_context, session)
    utils.create_context("files/fileSearchContext", file_search_context_2, session)
    utils.create_context("files/fileMaskContext", file_mask_context, session)
    utils.create_context("files/fileMaskContext", decrypt_file_mask_context, session)


def teardown(session):
    utils.destroy_context("searchContext", search_context_name, session)
    utils.destroy_context("maskContext", mask_context_name, session)
    utils.destroy_context("maskContext", decrypt_mask_context_name, session)
    utils.destroy_context("files/fileSearchContext", file_search_context_name, session)
    utils.destroy_context("files/fileSearchContext", file_search_context_2_name, session)
    utils.destroy_context("files/fileMaskContext", file_mask_context_name, session)
    utils.destroy_context("files/fileMaskContext", decrypt_file_mask_context_name, session)
