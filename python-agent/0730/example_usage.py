# -*- coding: utf-8 -*-
"""
Example usage of LLM PDF to Markdown tool
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.llm_pdf2md_tool import LLMPdf2MarkdownTool


def example_basic_usage():
    """Basic usage example"""
    print("=== Basic Usage Example ===")
    
    # Initialize the tool
    tool = LLMPdf2MarkdownTool(
        model_id="qwen-vl-plus",
        max_workers=5,
        max_retries=3
    )
    
    # Convert PDF to markdown
    pdf_path = "storage/test_pdf01.pdf"
    if Path(pdf_path).exists():
        result = tool.convert_pdf_to_markdown(pdf_path)
        
        if result['success']:
            print(f"✅ Conversion successful!")
            print(f"📄 Total pages: {result['total_pages']}")
            print(f"✅ Successful pages: {result['successful_pages']}")
            print(f"❌ Failed pages: {result['failed_pages']}")
            print(f"⏱️  Processing time: {result['processing_time_seconds']:.2f} seconds")
            
            # Save to file
            output_file = "storage/output_basic.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['combined_markdown'])
            print(f"💾 Markdown saved to: {output_file}")
        else:
            print(f"❌ Conversion failed: {result['error']}")
    else:
        print(f"❌ PDF file not found: {pdf_path}")


def example_custom_prompt():
    """Example with custom prompt"""
    print("\n=== Custom Prompt Example ===")
    
    tool = LLMPdf2MarkdownTool(
        model_id="qwen-vl-plus",
        max_workers=3,
        max_retries=2
    )
    
    custom_prompt = """
    请仔细分析图片中的内容，并以结构化的markdown格式输出：
    1. 识别标题和子标题
    2. 提取列表和表格
    3. 保持原始格式和结构
    4. 如果有代码块，请用代码块格式
    """
    
    pdf_path = "sample/test_pdf01.pdf"
    if Path(pdf_path).exists():
        result = tool.convert_pdf_to_markdown(
            pdf_path,
            start_page=1,
            end_page=2,  # Only first 2 pages
            prompt=custom_prompt
        )
        
        if result['success']:
            print(f"✅ Custom prompt conversion successful!")
            print(f"📄 Processed pages: {result['processed_pages']}")
            
            # Save to file
            output_file = "sample/output_custom_prompt.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['combined_markdown'])
            print(f"💾 Markdown saved to: {output_file}")
        else:
            print(f"❌ Conversion failed: {result['error']}")


def example_url_conversion():
    """Example with PDF URL"""
    print("\n=== URL Conversion Example ===")
    
    tool = LLMPdf2MarkdownTool(
        model_id="qwen-vl-plus",
        max_workers=4,
        max_retries=3
    )
    
    # Example PDF URL (replace with actual URL)
    pdf_url = "https://example.com/sample.pdf"
    
    print(f"⚠️  Note: This example uses a placeholder URL: {pdf_url}")
    print("To test with real URL, replace the URL in the code.")
    
    # Uncomment to test with real URL
    # result = tool.convert_pdf_url_to_markdown(pdf_url)
    # if result['success']:
    #     print(f"✅ URL conversion successful!")
    #     print(f"📄 Total pages: {result['total_pages']}")
    # else:
    #     print(f"❌ URL conversion failed: {result['error']}")


def example_error_handling():
    """Example showing error handling"""
    print("\n=== Error Handling Example ===")
    
    tool = LLMPdf2MarkdownTool(
        model_id="qwen-vl-plus",
        max_workers=2,
        max_retries=1
    )
    
    # Try with non-existent file
    result = tool.convert_pdf_to_markdown("non_existent.pdf")
    
    print(f"❌ Expected failure: {result['success']}")
    print(f"Error message: {result['error']}")


def example_performance_comparison():
    """Compare performance with different worker counts"""
    print("\n=== Performance Comparison ===")
    
    pdf_path = "sample/test_pdf01.pdf"
    if not Path(pdf_path).exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    worker_counts = [1, 3, 5]
    
    for workers in worker_counts:
        print(f"\n--- Testing with {workers} workers ---")
        
        tool = LLMPdf2MarkdownTool(
            model_id="qwen-vl-plus",
            max_workers=workers,
            max_retries=2
        )
        
        result = tool.convert_pdf_to_markdown(
            pdf_path,
            start_page=1,
            end_page=2  # Only first 2 pages for comparison
        )
        
        if result['success']:
            print(f"✅ Success with {workers} workers")
            print(f"⏱️  Processing time: {result['processing_time_seconds']:.2f} seconds")
            print(f"📄 Processed pages: {result['processed_pages']}")
        else:
            print(f"❌ Failed with {workers} workers: {result['error']}")


if __name__ == "__main__":
    print("LLM PDF to Markdown Tool - Usage Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_custom_prompt()
    example_url_conversion()
    example_error_handling()
    example_performance_comparison()
    
    print("\n" + "=" * 50)
    print("All examples completed!") 