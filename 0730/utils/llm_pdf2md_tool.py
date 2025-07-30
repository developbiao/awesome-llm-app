# -*- coding: utf-8 -*-
"""
PDF to Markdown conversion tool using LLM
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import getpass
from functools import wraps

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from agno.agent import Agent
from agno.media import Image
from agno.models.openai.like import OpenAILike

from utils.pdf2image_tool import pdf2imageTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Retry decorator for handling transient failures"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed. Last error: {e}")
            raise last_exception
        return wrapper
    return decorator


class LLMPdf2MarkdownTool:
    """PDF to Markdown conversion tool using LLM with concurrent processing"""
    
    def __init__(self, 
                 model_id: str = "qwen-vl-plus",
                 api_key: Optional[str] = None,
                 base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
                 temperature: float = 0.3,
                 max_workers: int = 10,
                 max_retries: int = 3,
                 base_storage_path: Optional[str] = None):
        """
        Initialize the PDF to Markdown tool
        
        Args:
            model_id: LLM model ID
            api_key: API key for the LLM service
            base_url: Base URL for the LLM service
            temperature: Temperature for LLM generation
            max_workers: Maximum number of concurrent workers
            max_retries: Maximum number of retries for failed requests
            base_storage_path: Base path for storing temporary files
        """
        self.model_id = model_id
        self.base_url = base_url
        self.temperature = temperature
        self.max_workers = max_workers
        self.max_retries = max_retries
        
        # Initialize API key
        if api_key is None:
            api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            api_key = getpass.getpass("Enter your DashScope API key: ")
            os.environ["DASHSCOPE_API_KEY"] = api_key
        self.api_key = api_key
        
        # Initialize PDF to image tool
        self.pdf2image_tool = pdf2imageTool(base_storage_path=base_storage_path)
        
        # Initialize LLM agent
        self.agent = self._create_agent()
        
        # Default prompt for image to markdown conversion
        self.default_prompt = "请将图片中的内容以markdown格式输出，不要包含任何其他内容"
    
    def _create_agent(self) -> Agent:
        """Create and return an LLM agent"""
        model_provider = OpenAILike(
            id=self.model_id,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=self.temperature,
        )
        return Agent(model=model_provider, markdown=True)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def _process_single_image(self, image_path: str, prompt: str = None) -> Dict[str, Any]:
        """
        Process a single image to markdown with retry mechanism
        
        Args:
            image_path: Path to the image file
            prompt: Custom prompt for conversion
            
        Returns:
            Dictionary containing page number and markdown content
        """
        if prompt is None:
            prompt = self.default_prompt
            
        try:
            # Create Image object from image path using filepath parameter
            image_obj = Image(filepath=Path(image_path))
            
            # Get page number from filename (assuming format: page_XXX.jpg)
            page_num = int(Path(image_path).stem.split('_')[1])
            
            # Process with LLM using images parameter
            run = self.agent.run(prompt, images=[image_obj])
            
            if run.content:
                return {
                    'page_num': page_num,
                    'content': run.content,
                    'status': 'success',
                    'image_path': image_path
                }
            else:
                raise ValueError("LLM response is empty")
                
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return {
                'page_num': int(Path(image_path).stem.split('_')[1]) if '_' in Path(image_path).stem else 0,
                'content': f"Error processing page: {str(e)}",
                'status': 'error',
                'image_path': image_path,
                'error': str(e)
            }
    
    def convert_pdf_to_markdown(self, 
                               pdf_path: str, 
                               start_page: int = 1, 
                               end_page: Optional[int] = None,
                               prompt: str = None,
                               sort_by_page: bool = True) -> Dict[str, Any]:
        """
        Convert PDF to markdown using concurrent processing
        
        Args:
            pdf_path: Path to the PDF file
            start_page: Starting page number (1-based)
            end_page: Ending page number (1-based, None for all pages)
            prompt: Custom prompt for LLM conversion
            sort_by_page: Whether to sort results by page number
            
        Returns:
            Dictionary containing conversion results and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Convert PDF to images
            logger.info(f"Converting PDF to images: {pdf_path}")
            image_paths = self.pdf2image_tool.convert_pdf_to_images(
                pdf_path, start_page, end_page
            )
            
            if not image_paths:
                raise ValueError("No images generated from PDF")
            
            logger.info(f"Generated {len(image_paths)} images from PDF")
            
            # Step 2: Process images concurrently with LLM
            logger.info(f"Processing {len(image_paths)} images with {self.max_workers} workers")
            
            results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_image = {
                    executor.submit(self._process_single_image, image_path, prompt): image_path
                    for image_path in image_paths
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_image):
                    image_path = future_to_image[future]
                    try:
                        result = future.result()
                        results.append(result)
                        logger.info(f"Completed processing: {image_path}")
                    except Exception as e:
                        logger.error(f"Error processing {image_path}: {e}")
                        results.append({
                            'page_num': int(Path(image_path).stem.split('_')[1]) if '_' in Path(image_path).stem else 0,
                            'content': f"Error: {str(e)}",
                            'status': 'error',
                            'image_path': image_path,
                            'error': str(e)
                        })
            
            # Step 3: Sort results by page number if requested
            if sort_by_page:
                results.sort(key=lambda x: x['page_num'])
            
            # Step 4: Combine all markdown content
            combined_markdown = self._combine_markdown_results(results)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'pdf_path': pdf_path,
                'total_pages': len(image_paths),
                'processed_pages': len(results),
                'processing_time_seconds': processing_time,
                'results': results,
                'combined_markdown': combined_markdown,
                'successful_pages': len([r for r in results if r['status'] == 'success']),
                'failed_pages': len([r for r in results if r['status'] == 'error'])
            }
            
        except Exception as e:
            logger.error(f"Error in PDF to markdown conversion: {e}")
            return {
                'success': False,
                'pdf_path': pdf_path,
                'error': str(e),
                'processing_time_seconds': time.time() - start_time
            }
    
    def _combine_markdown_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Combine individual page results into a single markdown document
        
        Args:
            results: List of page results
            
        Returns:
            Combined markdown content
        """
        combined_content = []
        
        for result in results:
            if result['status'] == 'success':
                # Add page header
                combined_content.append(f"\n## Page {result['page_num']}\n")
                combined_content.append(result['content'])
                combined_content.append("\n---\n")
            else:
                # Add error information
                combined_content.append(f"\n## Page {result['page_num']} - Error\n")
                combined_content.append(f"*Error processing this page: {result.get('error', 'Unknown error')}*\n")
                combined_content.append("\n---\n")
        
        return "\n".join(combined_content)
    
    def convert_pdf_url_to_markdown(self, 
                                   pdf_url: str, 
                                   start_page: int = 1, 
                                   end_page: Optional[int] = None,
                                   prompt: str = None) -> Dict[str, Any]:
        """
        Convert PDF from URL to markdown
        
        Args:
            pdf_url: URL of the PDF file
            start_page: Starting page number (1-based)
            end_page: Ending page number (1-based, None for all pages)
            prompt: Custom prompt for LLM conversion
            
        Returns:
            Dictionary containing conversion results and metadata
        """
        try:
            # Convert PDF URL to images
            image_paths = self.pdf2image_tool.convert_pdf_to_images_from_url(
                pdf_url, start_page, end_page
            )
            
            if not image_paths:
                raise ValueError("No images generated from PDF URL")
            
            # Process images concurrently
            results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_image = {
                    executor.submit(self._process_single_image, image_path, prompt): image_path
                    for image_path in image_paths
                }
                
                for future in as_completed(future_to_image):
                    image_path = future_to_image[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing {image_path}: {e}")
                        results.append({
                            'page_num': int(Path(image_path).stem.split('_')[1]) if '_' in Path(image_path).stem else 0,
                            'content': f"Error: {str(e)}",
                            'status': 'error',
                            'image_path': image_path,
                            'error': str(e)
                        })
            
            # Sort and combine results
            results.sort(key=lambda x: x['page_num'])
            combined_markdown = self._combine_markdown_results(results)
            
            return {
                'success': True,
                'pdf_url': pdf_url,
                'total_pages': len(image_paths),
                'processed_pages': len(results),
                'results': results,
                'combined_markdown': combined_markdown,
                'successful_pages': len([r for r in results if r['status'] == 'success']),
                'failed_pages': len([r for r in results if r['status'] == 'error'])
            }
            
        except Exception as e:
            logger.error(f"Error in PDF URL to markdown conversion: {e}")
            return {
                'success': False,
                'pdf_url': pdf_url,
                'error': str(e)
            }

