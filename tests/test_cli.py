import pytest
from click.testing import CliRunner
from lr_autotag.cli import main
from unittest.mock import patch, MagicMock

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_catalog_path(runner):
    with patch('lr_autotag.cli.LightroomClassicTagger') as MockTagger:
        mock_instance = MockTagger.return_value
        mock_instance.process_catalog.return_value = {}
        
        result = runner.invoke(main, ['--catalog', 'test.lrcat'])
        assert result.exit_code == 0
        MockTagger.assert_called_once_with('test.lrcat', None)

def test_cli_image_folder(runner):
    with patch('lr_autotag.cli.LightroomClassicTagger') as MockTagger:
        mock_instance = MockTagger.return_value
        mock_instance.process_catalog.return_value = {}
        
        result = runner.invoke(main, ['--image-folder', 'test/images'])
        assert result.exit_code == 0
        MockTagger.assert_called_once_with(None, 'test/images')

def test_cli_overwrite_flag(runner):
    with patch('lr_autotag.cli.LightroomClassicTagger') as MockTagger:
        mock_instance = MockTagger.return_value
        mock_instance.process_catalog.return_value = {}
        
        result = runner.invoke(main, ['--catalog', 'test.lrcat', '--overwrite'])
        assert result.exit_code == 0
        mock_instance.process_catalog.assert_called_once_with('keyword_suggestions.json', True)

def test_cli_custom_output(runner):
    with patch('lr_autotag.cli.LightroomClassicTagger') as MockTagger:
        mock_instance = MockTagger.return_value
        mock_instance.process_catalog.return_value = {}
        
        result = runner.invoke(main, ['--catalog', 'test.lrcat', '--output', 'custom.json'])
        assert result.exit_code == 0
        mock_instance.process_catalog.assert_called_once_with('custom.json', False)