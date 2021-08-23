import logging
import os
import pathlib

host = 'http://localhost:8080/api/darkshield'

def create_context(context, data, session):
    url = f'{host}/{context}.create'
    logging.info(f'POST: {url}')
    with session.post(url, json=data) as r:
        if r.status_code >= 300:
            raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")


def destroy_context(context, name,session):
    url = f'{host}/{context}.destroy'
    logging.info(f'POST: {url}')
    session.post(url, json={'name': name})


def download_model(name,session):
    current_dir = pathlib.Path(__file__).parent.absolute()
    model_path = current_dir.joinpath(name)
    logging.info(f'Checking if {model_path} exists')
    if not model_path.exists():
        logging.info(f'{model_path} does not exist, downloading...')
        with session.get(f'http://opennlp.sourceforge.net/models-1.5/{name}') as r:
            if r.status_code != 200:
                raise Exception(f'Could not download "{name}", failed with status {r.status_code}:\n\n{r.text}')
            with open(model_path, 'wb') as f:
                f.write(r.content)
                logging.info(f'Downloaded {name}')

    return model_path.as_uri()
