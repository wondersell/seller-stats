from abc import abstractmethod
from csv import DictReader

from envparse import ConfigurationError, env
from scrapinghub import ScrapinghubClient

from .transformers import EmptyTransformer, Transformer


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
            self.client = client or ScrapinghubClient(env('SCRAPINGHUB_API_KEY'))
        except ConfigurationError:
            raise ConfigurationError('Scrapinghub init failed. Pass scrapinghub client or set SCRAPINGHUB_API_KEY env.')

        super().__init__(transformer=transformer)

    def load(self):
        return [self.transformer.transform_item(item) for item in self.client.get_job(self.job_id).items.iter()]


class CsvLoader(Loader):
    def __init__(self, file_path: str, reader: DictReader = None, transformer: Transformer = None):
        self.file_path = file_path
        self.reader = reader or DictReader(open(self.file_path, 'r'))

        super().__init__(transformer=transformer)

    def load(self):
        return [self.transformer.transform_item(item) for item in self.reader]
