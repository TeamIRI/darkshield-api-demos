import json
import logging
import simplejson as json
import utils

from botocore import exceptions

host = 'http://localhost:8080/api/darkshield'
search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"

def create_table(dynamodb, table_name):
  logging.info(f'Attempting to create {table_name}...')
  table = dynamodb.create_table(
    TableName=table_name,
    KeySchema=[
      {
        'AttributeName': 'id',
        'KeyType': 'HASH' # Partition key
      }
    ],
    AttributeDefinitions=[
      {
        'AttributeName': 'id',
        'AttributeType': 'N' 
      }
    ],
    ProvisionedThroughput={
      'ReadCapacityUnits': 10,
      'WriteCapacityUnits': 10
    }
  )
  table.wait_until_exists()
  logging.info(f'Succesfully created {table_name}')
  return table


def delete_table(table):
  try:
    logging.info(f"Deleting '{table.name}' if it does not exist...")
    table.delete()
    table.wait_until_not_exists()
  except exceptions.ClientError as e:
    if e.response['Error']['Code'] == 'ResourceNotFoundException':
      logging.info(f"'{table.name}' does not exist.")
    else:
      raise e


def populate_test_data(table):
  with open('data.json') as f:
    data = json.load(f)

  logging.info(f'Loading data.json...')
  for item in data:
    table.put_item(Item=item)
  logging.info(f'Loaded data.json.')


def setup():
    model_url = utils.download_model('en-ner-person.bin')
    sent_url = utils.download_model('en-sent.bin')
    token_url = utils.download_model('en-token.bin')
    
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
          "sentenceDetectorUrl": sent_url,
          "tokenizerUrl": token_url
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
          "pattern": "PhoneMatcher|NameMatcher"
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
