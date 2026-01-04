# -*- coding: utf-8 -*-
"""
Pytest tests for LLM PDF to Markdown tool
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.llm_pdf2md_tool import LLMPdf2MarkdownTool, retry_on_failure


class TestLLMPdf2MarkdownTool:
    """Test class for LLMPdf2MarkdownTool"""
    
    @pytest.fixture
    def tool(self):
        """Create a test instance of LLMPdf2MarkdownTool"""
        with patch('utils.llm_pdf2md_tool.getpass.getpass') as mock_getpass:
            mock_getpass.return_value = "test_api_key"
            return LLMPdf2MarkdownTool(
                model_id="qwen-vl-plus",
                api_key="test_api_key",
                max_workers=2,
                max_retries=2
            )
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Get sample PDF path"""
        pdf_path = Path("storage/sample/test_pdf01.pdf")
        if not pdf_path.exists():
            pytest.skip(f"Sample PDF not found: {pdf_path}")
        return str(pdf_path)
    
    def test_initialization(self, tool):
        """Test tool initialization"""
        assert tool.model_id == "qwen-vl-plus"
        assert tool.api_key == "test_api_key"
        assert tool.max_workers == 2
        assert tool.max_retries == 2
        assert tool.default_prompt is not None
    
    def test_create_agent(self, tool):
        """Test agent creation"""
        agent = tool._create_agent()
        assert agent is not None
    
    @patch('utils.llm_pdf2md_tool.Image')
    @patch('utils.llm_pdf2md_tool.Path')
    def test_process_single_image_success(self, mock_path, mock_image, tool):
        """Test successful single image processing"""
        # Mock image path
        mock_path_instance = Mock()
        mock_path_instance.read_bytes.return_value = b"fake_image_bytes"
        mock_path_instance.stem = "page_001"
        mock_path.return_value = mock_path_instance
        
        # Mock image
        mock_image_instance = Mock()
        mock_image.return_value = mock_image_instance
        
        # Mock agent run
        mock_run = Mock()
        mock_run.content = "# Test Markdown Content"
        tool.agent.run = Mock(return_value=mock_run)
        
        # Test processing
        result = tool._process_single_image("fake_image_path.jpg")
        
        assert result['page_num'] == 1
        assert result['content'] == "# Test Markdown Content"
        assert result['status'] == 'success'
        assert result['image_path'] == "fake_image_path.jpg"
    
    @patch('utils.llm_pdf2md_tool.Image')
    @patch('utils.llm_pdf2md_tool.Path')
    def test_process_single_image_error(self, mock_path, mock_image, tool):
        """Test single image processing with error"""
        # Mock image path
        mock_path_instance = Mock()
        mock_path_instance.read_bytes.side_effect = Exception("File not found")
        mock_path_instance.stem = "page_001"
        mock_path.return_value = mock_path_instance
        
        # Mock Image to raise exception
        mock_image.side_effect = Exception("Image creation failed")
        
        # Test processing
        result = tool._process_single_image("fake_image_path.jpg")
        
        assert result['page_num'] == 1
        assert result['status'] == 'error'
        assert 'Image creation failed' in result['content']
    
    def test_combine_markdown_results(self, tool):
        """Test markdown results combination"""
        results = [
            {
                'page_num': 1,
                'content': '# Page 1 Content',
                'status': 'success'
            },
            {
                'page_num': 2,
                'content': '# Page 2 Content',
                'status': 'success'
            },
            {
                'page_num': 3,
                'content': 'Error message',
                'status': 'error',
                'error': 'Processing failed'
            }
        ]
        
        combined = tool._combine_markdown_results(results)
        
        assert '## Page 1' in combined
        assert '## Page 2' in combined
        assert '## Page 3 - Error' in combined
        assert 'Page 1 Content' in combined
        assert 'Page 2 Content' in combined
        assert 'Processing failed' in combined
    
    @patch('utils.llm_pdf2md_tool.pdf2imageTool')
    def test_convert_pdf_to_markdown_success(self, mock_pdf2image, tool, sample_pdf_path):
        """Test successful PDF to markdown conversion"""
        # Mock PDF to image conversion
        mock_tool_instance = Mock()
        mock_tool_instance.convert_pdf_to_images.return_value = [
            "page_001.jpg",
            "page_002.jpg"
        ]
        tool.pdf2image_tool = mock_tool_instance
        
        # Mock single image processing
        with patch.object(tool, '_process_single_image') as mock_process:
            mock_process.side_effect = [
                {
                    'page_num': 1,
                    'content': '# Page 1 Content',
                    'status': 'success',
                    'image_path': 'page_001.jpg'
                },
                {
                    'page_num': 2,
                    'content': '# Page 2 Content',
                    'status': 'success',
                    'image_path': 'page_002.jpg'
                }
            ]
            
            result = tool.convert_pdf_to_markdown(sample_pdf_path)
            
            assert result['success'] is True
            assert result['total_pages'] == 2
            assert result['processed_pages'] == 2
            assert result['successful_pages'] == 2
            assert result['failed_pages'] == 0
            assert 'Page 1 Content' in result['combined_markdown']
            assert 'Page 2 Content' in result['combined_markdown']
    
    @patch('utils.llm_pdf2md_tool.pdf2imageTool')
    def test_convert_pdf_to_markdown_no_images(self, mock_pdf2image, tool, sample_pdf_path):
        """Test PDF to markdown conversion with no images generated"""
        # Mock PDF to image conversion returning empty list
        mock_tool_instance = Mock()
        mock_tool_instance.convert_pdf_to_images.return_value = []
        tool.pdf2image_tool = mock_tool_instance
        
        result = tool.convert_pdf_to_markdown(sample_pdf_path)
        
        assert result['success'] is False
        assert 'No images generated' in result['error']
    
    def test_retry_decorator(self):
        """Test retry decorator functionality"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.1)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "Success"
        
        # Should succeed on third attempt
        result = failing_function()
        assert result == "Success"
        assert call_count == 3
    
    def test_retry_decorator_max_retries_exceeded(self):
        """Test retry decorator when max retries are exceeded"""
        call_count = 0
        
        @retry_on_failure(max_retries=2, delay=0.1)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        # Should raise exception after max retries
        with pytest.raises(ValueError, match="Always fails"):
            always_failing_function()
        assert call_count == 2


class TestIntegration:
    """Integration tests (require actual PDF file)"""
    
    # Usage: python -m pytest test_llm_pdf2md_tool.py -v
    @pytest.mark.integration
    def test_real_pdf_conversion(self):
        """Test with real PDF file (requires API key)"""
        pdf_path = Path("storage/sample/test_pdf01.pdf")
        if not pdf_path.exists():
            pytest.skip(f"Sample PDF not found: {pdf_path}")
        
        # Skip if no API key
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            pytest.skip("No DASHSCOPE_API_KEY environment variable")
        
        tool = LLMPdf2MarkdownTool(
            model_id="qwen-vl-plus",
            api_key=api_key,
            max_workers=2,
            max_retries=2
        )
        
        result = tool.convert_pdf_to_markdown(
            str(pdf_path),
            start_page=1,
            end_page=1  # Test only first page
        )
        
        assert result['success'] is True
        assert result['total_pages'] >= 1
        assert result['processed_pages'] >= 1
        assert len(result['combined_markdown']) > 0
        # print the result
        print(result['combined_markdown'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 