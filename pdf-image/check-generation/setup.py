import pathlib

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
                "name": "noMatcher",
                "type": "pattern",
                "pattern": r""
            }
        ]
    }

    mask_context = {
        "name": mask_context_name,
        "rules": [
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
        ],
        "configs": {
            "image": {
                "useOCR": False
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
        ],
        "configs": {
            "image": {
                "boundingBoxes": [
                    "0.018867924528301886,0.015810276679841896,0.22039451114922812,0.11462450592885376",  # name
                    "0.022298456260720412,0.1225296442687747,0.22495711835334476,0.17053359683794467",  # street address
                    "0.022298456260720412,0.17253359683794467,0.20553359683794467,0.22495711835334476",
                    # city, state and zip
                    "0.060034305317324184,0.8181818181818182,0.2624356775300172,0.9090909090909091",  # routing number
                    "0.30017152658662094,0.8142292490118577,0.5111492281303602,0.8972332015810277"  # account number
                ],
                "maskingMethod": "replace",
                "setReplacement": [
                    pathlib.Path('myset.set').absolute().as_uri(), pathlib.Path('myset.set').absolute().as_uri(),
                    pathlib.Path('city-state-zip.set').absolute().as_uri(),
                    pathlib.Path('routing-number.set').absolute().as_uri(),
                    pathlib.Path('account-number.set').absolute().as_uri()
                ],
                "setReplacementColumns": [
                    0, 1, 0, 0, 0
                ],
                "copyBackground": True
            }
        }
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
