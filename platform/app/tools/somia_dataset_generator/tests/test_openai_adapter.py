import base64
from unittest.mock import MagicMock, patch

from somia_dataset_generator.openai_adapter import OpenAIImageAdapter


def test_generate_decodes_base64_image_and_returns_revised_prompt():
    fake_item = MagicMock()
    fake_item.b64_json = base64.b64encode(b"raw-image-bytes").decode("ascii")
    fake_item.revised_prompt = "a revised prompt"
    fake_response = MagicMock()
    fake_response.data = [fake_item]

    with patch("somia_dataset_generator.openai_adapter.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.images.generate.return_value = fake_response
        mock_openai_cls.return_value = mock_client

        adapter = OpenAIImageAdapter(api_key="test-key")
        result = adapter.generate(
            prompt="a prompt", model="gpt-image-1", size="1024x1536", quality="high", output_format="png"
        )

    assert result.image_bytes == b"raw-image-bytes"
    assert result.revised_prompt == "a revised prompt"
    mock_client.images.generate.assert_called_once_with(
        model="gpt-image-1", prompt="a prompt", size="1024x1536", quality="high", output_format="png", n=1,
    )


def test_generate_raises_when_no_image_data_returned():
    fake_item = MagicMock()
    fake_item.b64_json = None
    fake_response = MagicMock()
    fake_response.data = [fake_item]

    with patch("somia_dataset_generator.openai_adapter.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.images.generate.return_value = fake_response
        mock_openai_cls.return_value = mock_client

        adapter = OpenAIImageAdapter(api_key="test-key")
        try:
            adapter.generate(prompt="p", model="m", size="s", quality="q", output_format="png")
        except RuntimeError as exc:
            assert "no base64 image data" in str(exc)
        else:
            raise AssertionError("expected RuntimeError")
