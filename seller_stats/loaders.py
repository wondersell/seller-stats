import logging
from abc import abstractmethod
from csv import DictReader

from envparse import ConfigurationError, env
from scrapinghub import ScrapinghubClient

from .transformers import EmptyTransformer, Transformer

logger = logging.getLogger(__name__)


class Loader:
    def __init__(self, transformer: Transformer = None):
        self.transformer = transformer or EmptyTransformer()

    @abstractmethod
    def load(self):
        pass


class ScrapinghubLoader(Loader):
    def __init__(self, job_id: str, client: ScrapinghubClient = None, transformer: Transformer = None):
        self.job_id = job_id

        try:
            self.client = client or ScrapinghubClient(env('SH_APIKEY'))
        except ConfigurationError:
            raise ConfigurationError('Scrapinghub init failed. Pass scrapinghub client or set SH_APIKEY env.')

        logger.info(f'Loading items from scrapinghub job {job_id}')

        super().__init__(transformer=transformer)

    def load(self):
        items = [self.transformer.transform_item(item) for item in self.client.get_job(self.job_id).items.iter()]

        logger.info(f'Loaded {len(items)} items from scrapinghub')

        return items


class CsvLoader(Loader):
    def __init__(self, file_path: str, reader: DictReader = None, transformer: Transformer = None):
        self.file_path = file_path
        self.reader = reader or DictReader(open(self.file_path, 'r'))

        logger.info(f'Loading items from CSV file {file_path}')

        super().__init__(transformer=transformer)

    def load(self):
        items = [self.transformer.transform_item(item) for item in self.reader]

        logger.info(f'Loaded {len(items)} items from CSV')

        return items
