# -*- coding: utf-8 -*-
import fitz
import os
import uuid
import datetime
import requests
from PIL import Image
import io

from utils.file_downloader_tool import FileDownloaderTool

# PDF 文件转换为图片工具
class pdf2imageTool:
    def __init__(self, base_storage_path = None, quality = 75):
        # if base_path is None
        if base_storage_path is None:
            self.base_path = 'storage'
        else:
            # if base_path is not None automatically set base_path to storage
            self.base_path = base_storage_path

        # Set image quality
        self.quality = quality

    # 从 pdf url 下载 pdf 文件并转换为图片
    # Convert pdf to images from url
    def convert_pdf_to_images_from_url(self, pdf_url, start_page=1, end_page=None):
        # 1. Download pdf file from pdf url and save to temp folder
        # 从pdf url下载pdf文件并保存到临时文件夹
        today = datetime.date.today()
        date_path = today.strftime('%Y/%m/%d')
        temp_folder_path = os.path.join(self.base_path, 'downloads', date_path)
        os.makedirs(temp_folder_path, exist_ok=True)

        temp_name = str(uuid.uuid4())[:8] + '.pdf'
        pdf_path = os.path.join(temp_folder_path, temp_name)

        # Download pdf file from url
        # 从url下载pdf文件
        file_downloader_tool = FileDownloaderTool()
        pdf_path = file_downloader_tool.download_pdf(pdf_url)

        # 2. Convert pdf to images
        return self.convert_pdf_to_images(pdf_path, start_page, end_page)

    # Download pdf file from url
    def download_pdf(self, pdf_url, pdf_path):
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()  # Check for any HTTP errors
            with open(pdf_path, 'wb') as file:
                file.write(response.content)
            return pdf_path
        except requests.exceptions.RequestException as e:
            print(f"Error downloading PDF: {e}")
            raise Exception(f"Error downloading PDF: {e}")

    # Convert pdf to images
    def convert_pdf_to_images(self, pdf_path, start_page=1, end_page=None):
        images = []
        doc = fitz.open(pdf_path)
        today = datetime.date.today()

        # Calcuate pdf file md5
        pdf_md5 = FileDownloaderTool().calculate_file_md5(pdf_path)

        # Generate image folder
        date_path = today.strftime('%Y/%m/%d')
        folder_path = f"{self.base_path}/pdf2images/{date_path}/{pdf_md5}"

        # Generate image temp folder
        os.makedirs(folder_path, exist_ok=True)

        # Adjust the end page if not provided or out of range
        if end_page is None or end_page < 1 or end_page > len(doc):
            end_page = len(doc)

        # Adjust the start page if out of range
        if start_page is None or start_page < 1:
            start_page = 1
        # Adjust the start page if out of range
        if start_page < 1:
            start_page = 1

        # Ensure start_page and end_page are within the document's range
        start_page = max(1, min(start_page, len(doc)))
        end_page = max(1, min(end_page, len(doc)))

        for page_num in range(start_page - 1, end_page):
            try:
                page = doc.load_page(page_num)
                # Generate unique file name
                output_image_format = 'page_{:03d}.jpg'
                image_path = os.path.join(folder_path, output_image_format.format(page_num + 1))

                # # Generate the image
                # pix = page.get_pixmap(matrix=fitz.Matrix(3.5, 3.5))
                # # Save the image with specified quality
                # pix.save(image_path, "jpeg", quality=50)
                # images.append(image_path)
                 # Generate the image

                # pix = page.get_pixmap(matrix=fitz.Matrix(3.5, 3.5))
                pix = page.get_pixmap()

                # Convert pixmap to PIL Image
                img = Image.open(io.BytesIO(pix.tobytes("ppm")))

                # Convert to grayscale
                # img = img.convert("L")

                # Save the image with specified quality
                img.save(image_path, "JPEG", quality=80)
                images.append(image_path)

            except IndexError:
                print(f"Page {page_num + 1} is out of range.")
                break

        doc.close()

        return images
