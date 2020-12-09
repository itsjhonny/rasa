import os
import typing
from typing import Any, Dict, List, Optional, Text

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig, override_defaults
from rasa.shared.core.domain import Domain

if typing.TYPE_CHECKING:
    import mitie
    from rasa.nlu.model import Metadata


class MitieNLP(Component):

    defaults = {
        # name of the language model to load - this contains
        # the MITIE feature extractor
        "model": os.path.join("data", "total_word_feature_extractor.dat")
    }

    def __init__(
        self, component_config: Optional[Dict[Text, Any]] = None, extractor=None
    ) -> None:
        """Construct a new language model from the MITIE framework."""

        super().__init__(component_config)

        self.extractor = extractor

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["mitie"]

    @classmethod
    def create(
        cls,
        component_config: Dict[Text, Any],
        model_config: RasaNLUModelConfig,
        domain: Optional[Domain] = None,
    ) -> "MitieNLP":
        """Creates this component (e.g. before a training is started)."""
        import mitie

        component_config = override_defaults(cls.defaults, component_config)

        model_file = component_config.get("model")
        if not model_file:
            raise Exception(
                "The MITIE component 'MitieNLP' needs "
                "the configuration value for 'model'."
                "Please take a look at the "
                "documentation in the pipeline section "
                "to get more info about this "
                "parameter."
            )
        extractor = mitie.total_word_feature_extractor(model_file)
        cls.ensure_proper_language_model(extractor)

        return cls(component_config, extractor)

    @classmethod
    def cache_key(
        cls, component_meta: Dict[Text, Any], model_metadata: "Metadata"
    ) -> Optional[Text]:
        """This key is used to cache components."""
        mitie_file = component_meta.get("model", None)
        if mitie_file is not None:
            return cls.name + "-" + str(os.path.abspath(mitie_file))
        else:
            return None

    def provide_context(self) -> Dict[Text, Any]:

        return {
            "mitie_feature_extractor": self.extractor,
            "mitie_file": self.component_config.get("model"),
        }

    @staticmethod
    def ensure_proper_language_model(
        extractor: Optional["mitie.total_word_feature_extractor"],
    ) -> None:

        if extractor is None:
            raise Exception(
                "Failed to load MITIE feature extractor. "
                "Loading the model returned 'None'."
            )

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["MitieNLP"] = None,
        **kwargs: Any,
    ) -> "MitieNLP":
        import mitie

        if cached_component:
            return cached_component

        mitie_file = meta.get("model")
        return cls(meta, mitie.total_word_feature_extractor(mitie_file))

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:

        return {
            "mitie_feature_extractor_fingerprint": self.extractor.fingerprint,
            "model": self.component_config.get("model"),
        }
