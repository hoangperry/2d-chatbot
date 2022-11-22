import logging
from abc import ABC, abstractmethod, ABCMeta

import google.cloud.dialogflow_v2 as dialogflow
import hydra
from google.oauth2 import service_account
from omegaconf import DictConfig

from helper.utils import id_generator

log = logging.getLogger(__name__)


class ChatbotSession(metaclass=ABCMeta):
    @abstractmethod
    def chat(self, text: str):
        pass

    @abstractmethod
    def refresh(self):
        pass


@hydra.main(version_base=None, config_path='../config', config_name="dialogflow")
def test_config_loaded(config: DictConfig):
    print(config.audio_config)


class GoogleDialogflowSession(ChatbotSession):
    def __init__(self, cfg: DictConfig):
        self._project_id = cfg.project_id
        self._credentials = service_account.Credentials.from_service_account_file(cfg.credentials_file)
        self._session_client = dialogflow.SessionsClient(credentials=self._credentials)
        self._session_id = id_generator()
        self._session = self._session_client.session_path(cfg.project_id, self._session_id)
        self.language_code = cfg.language_code
        self.audio_config = cfg.audio_config

    # noinspection PyTypeChecker
    def create_input(self, text) -> dialogflow.types.TextInput:
        gg_text_input = dialogflow.types.TextInput(text=text, language_code=self.language_code)
        return dialogflow.types.QueryInput(text=gg_text_input, audio_config=self.audio_config)

    def detect_intent(self, query_input):
        return self._session_client.detect_intent(session=self._session, query_input=query_input)

    def chat(self, text: str) -> str:
        query_input = self.create_input(text)
        intent_response = self.detect_intent(query_input)
        return intent_response.query_result.fulfillment_text

    def refresh(self):
        self._session_id = id_generator()
        self._session = self._session_client.session_path(self._project_id, self._session_id)
