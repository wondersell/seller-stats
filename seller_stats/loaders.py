from scrapinghub import ScrapinghubClient
from envparse import env


def load_scrapinghub(job_id: str, client: ScrapinghubClient = None, keys: dict = None) -> list:
    if client is None:
        client = ScrapinghubClient(env('SCRAPINGHUB_API_KEY'))

    data = [item for item in client.get_job(job_id).items.iter()]

    if keys is not None:
        data = transform_keys(data, keys)

    return data


def load_csv() -> dict:
    pass


def transform_keys(data: list, rules: dict) -> list:
    for item in data:
        for key in rules.keys():
            if key in item.keys():
                item[rules[key]] = item.pop(key)

    return data
