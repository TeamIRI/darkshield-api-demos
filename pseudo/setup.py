import pathlib
import utils

search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"
reverse_pseudo_file_mask_context_name = "reversePseudoFileMaskContext"
reverse_pseudo_mask_context_name = "reversePseudoMaskContext"


def setup(session, args):
    search_context = {
        "name": search_context_name,
        "matchers": [
            {
                "name": "NameMatcher",
                "type": "set",
                "url": pathlib.Path('names_replace.set').absolute().as_uri(),
                "ignoreCase": True,
                "matchWholeWords": True
            }
        ]
    }

    mask_context = {
        "name": mask_context_name,
        "rules": [
            {
                "name": "PseudoRule",
                "type": "cosort",
                "setPath": f'{str(pathlib.Path("names_replace.set").absolute())} [IN]'
            }
        ],
        "ruleMatchers": [
            {
                "name": "PseudoRuleMatcher",
                "type": "name",
                "rule": "PseudoRule",
                "pattern": "NameMatcher"
            },
        ]
    }

    reverse_pseudo_mask_context = {
        "name": reverse_pseudo_mask_context_name,
        "rules": [
            {
                "name": "RestoreRule",
                "type": "cosort",
                "setPath": f'{str(pathlib.Path("names_revert.set").absolute())} [IN]'
            },
        ],
        "ruleMatchers": [
            {
                "name": "RestoreRuleMatcher",
                "type": "name",
                "rule": "RestoreRule",
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

    reverse_pseudo_file_mask_context = {
        "name": reverse_pseudo_file_mask_context_name,
        "rules": [
            {
                "name": reverse_pseudo_mask_context_name,
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
    utils.create_context("files/fileSearchContext", file_search_context, session)
    utils.create_context("maskContext", mask_context, session)
    utils.create_context("files/fileMaskContext", file_mask_context, session)
    utils.create_context("maskContext", reverse_pseudo_mask_context, session)
    utils.create_context("files/fileMaskContext", reverse_pseudo_file_mask_context, session)


def teardown(session):
    utils.destroy_context("searchContext", search_context_name, session)
    utils.destroy_context("maskContext", mask_context_name, session)
    utils.destroy_context("files/fileSearchContext", file_search_context_name, session)
    utils.destroy_context("files/fileMaskContext", file_mask_context_name, session)
    utils.destroy_context("files/fileMaskContext", reverse_pseudo_file_mask_context_name, session)
    utils.destroy_context("maskContext", reverse_pseudo_mask_context_name, session)
