# -*- coding: utf-8 -*-
"""
Test PDF to Markdown conversion tool
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.llm_pdf2md_tool import LLMPdf2MarkdownTool


def test_pdf_to_markdown():
    """Test PDF to Markdown conversion"""
    
    # Initialize the tool
    tool = LLMPdf2MarkdownTool(
        model_id="qwen-vl-plus",
        max_workers=5,  # Use 5 workers for testing
        max_retries=3
    )
    
    # Test PDF file path
    # pdf_path = Path("storage/sample/test_pdf01.pdf")
    pdf_path = Path("storage/sample/test_301_pdf.pdf")
    
    if not pdf_path.exists():
        print(f"PDF file not found: {pdf_path}")
        return
    
    print(f"Testing PDF to Markdown conversion: {pdf_path}")
    print("=" * 50)
    
    # Test conversion
    start_time = time.time()
    result = tool.convert_pdf_to_markdown(
        pdf_path=str(pdf_path),
        start_page=1,
        end_page=None,  # Process all pages
        prompt="请将图片中的内容以markdown格式输出，不要包含任何其他内容"
    )
    
    processing_time = time.time() - start_time
    
    # Print results
    print(f"Conversion completed in {processing_time:.2f} seconds")
    print(f"Success: {result.get('success', False)}")
    print(f"Total pages: {result.get('total_pages', 0)}")
    print(f"Processed pages: {result.get('processed_pages', 0)}")
    print(f"Successful pages: {result.get('successful_pages', 0)}")
    print(f"Failed pages: {result.get('failed_pages', 0)}")
    
    if result.get('success'):
        print("\nCombined Markdown Output:")
        print("=" * 50)
        print(result.get('combined_markdown', ''))
        
        # Save markdown to file
        output_file = Path("storage/sample/output_markdown.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.get('combined_markdown', ''))
        print(f"\nMarkdown saved to: {output_file}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")


def test_single_page_conversion():
    """Test single page conversion"""
    
    tool = LLMPdf2MarkdownTool(
        model_id="qwen-vl-plus",
        max_workers=1,
        max_retries=3
    )
    
    pdf_path = Path("storage/sample/test_pdf01.pdf")
    
    if not pdf_path.exists():
        print(f"PDF file not found: {pdf_path}")
        return
    
    print(f"Testing single page conversion: {pdf_path}")
    print("=" * 50)
    
    # Test first page only
    result = tool.convert_pdf_to_markdown(
        pdf_path=str(pdf_path),
        start_page=1,
        end_page=1,
        prompt="请将图片中的内容以markdown格式输出，不要包含任何其他内容"
    )
    
    print(f"Success: {result.get('success', False)}")
    print(f"Total pages: {result.get('total_pages', 0)}")
    
    if result.get('success'):
        print("\nFirst Page Markdown:")
        print("=" * 30)
        print(result.get('combined_markdown', ''))
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    import time
    print("Testing PDF to Markdown Conversion Tool")
    print("=" * 60)

    # Test single page conversion
    # test_single_page_conversion()
    
    # Test full PDF conversion
    start_time = time.time()
    test_pdf_to_markdown()
    spend_time = time.time() - start_time
    print(f"\nSpend time: {spend_time:.2f} seconds")
    
    print("\n" + "=" * 60)

