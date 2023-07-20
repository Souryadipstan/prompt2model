"""Testing description-based model retriever."""

import numpy as np
import pickle
import tempfile
from unittest.mock import patch

from prompt2model.model_retriever import DescriptionModelRetriever
from prompt2model.prompt_parser import MockPromptSpec, TaskType

TINY_MODEL_NAME = "google/bert_uncased_L-2_H-128_A-2"


def test_initialize_model_retriever():
    """Test loading a small Tevatron model."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
        retriever = DescriptionModelRetriever(
            search_index_path = f.name,
            search_depth = 5,
            model_name = TINY_MODEL_NAME,
            model_descriptions_index = "huggingface_models/model_info_tiny/"
        )
        assert len(retriever.model_names) == len(retriever.model_descriptions)
        # This tiny directory of HuggingFace models contains 3 models.
        assert len(retriever.model_descriptions) == 3

def test_encode_model_retriever():
    """Test loading a small Tevatron model."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pkl") as f:
        retriever = DescriptionModelRetriever(
            search_index_path = f.name,
            search_depth = 5,
            model_name = TINY_MODEL_NAME,
            model_descriptions_index = "huggingface_models/model_info_tiny/"
        )
        mock_prompt = MockPromptSpec(task_type=TaskType.TEXT_GENERATION)
        model_vectors = retriever.encode_model_descriptions(mock_prompt)
        assert model_vectors.shape == (3, 128)

@patch("prompt2model.model_retriever.description_based_retriever.encode_text", return_value=np.array([[0, 0, 1]]))
def test_retrieve_model_from_query_when_similarity_threshold_is_met(mock_encode_text):
    """Test loading a small Tevatron model."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pkl") as f:
        retriever = DescriptionModelRetriever(
            search_index_path = f.name,
            search_depth = 2,
            model_name = TINY_MODEL_NAME,
            model_descriptions_index = "huggingface_models/model_info_tiny/"
        )

        mock_model_encodings = np.array([[1, 0, 0], [0, 0.1, 0.9], [0, 0, 1]])
        mock_lookup_indices = [0, 1, 2, 3]
        with open(f.name, "wb") as f:
            pickle.dump((mock_model_encodings, mock_lookup_indices), f)

        mock_prompt = MockPromptSpec(task_type=TaskType.TEXT_GENERATION)
        top_model_name = retriever.retrieve(mock_prompt)
        assert mock_encode_text.call_count == 1
        # The 3rd item in the index is the closest to the query.
        assert top_model_name == retriever.model_names[2]


@patch("prompt2model.model_retriever.description_based_retriever.encode_text", return_value=np.array([[0, 0, 1]]))
def test_retrieve_model_from_query_when_similarity_threshold_is_not_met(mock_encode_text):
    """Test loading a small Tevatron model."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pkl") as f:
        retriever = DescriptionModelRetriever(
            search_index_path = f.name,
            search_depth = 2,
            model_name = TINY_MODEL_NAME,
            model_descriptions_index = "huggingface_models/model_info_tiny/"
        )

        mock_model_encodings = np.array([[1, 0, 0], [0, 0.1, 0.9], [0, 0, 1]])
        mock_lookup_indices = [0, 1, 2, 3]
        with open(f.name, "wb") as f:
            pickle.dump((mock_model_encodings, mock_lookup_indices), f)

        mock_prompt = MockPromptSpec(task_type=TaskType.TEXT_GENERATION)
        top_model_name = retriever.retrieve(mock_prompt)
        assert mock_encode_text.call_count == 1
        # The 3rd item in the index is the closest to the query.
        assert top_model_name == retriever.model_names[2]
