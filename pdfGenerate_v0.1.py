import os
import svgwrite
import asyncio
import PyPDF2
from pyppeteer import launch
# from PyPDF2 import PdfReader, PdfWriter
# from pdfrw import PdfReader, PdfWriter, PageMerge

def create_front_card_svg(filename, width, height, font_path, font_name):
    dwg = svgwrite.Drawing(filename, profile='full', size=(width, height))
    rect = dwg.rect(insert=(0, 0), size=(width, height), fill='white', stroke='black', stroke_width=1)
    dwg.add(rect)

    # 커스텀 폰트 및 스타일 정의
    style = f'@font-face {{ font-family: {font_name}; src: url("{os.path.basename(font_path)}"); }}'
    dwg.defs.add(dwg.style(style))

    # 텍스트 추가
    company = dwg.text("주식회사 Sample Company", insert=('50%', '50%'), font_size=14, fill='black', font_family=font_name, text_anchor="middle")
    dwg.add(company)
    dwg.save()

def create_back_card_svg(filename, width, height, font_path, font_name, height_mm):
    dwg = svgwrite.Drawing(filename, profile='full', size=(width, height))
    rect = dwg.rect(insert=(0, 0), size=(width, height), fill='white', stroke='black', stroke_width=1)
    dwg.add(rect)

    # 커스텀 폰트 및 스타일 정의
    style = f'@font-face {{ font-family: {font_name}; src: url("{font_path}"); }}'
    dwg.defs.add(dwg.style(style))

    # 텍스트 추가
    company = dwg.text("Sample Company", insert=(20, height_mm * 0.5), font_size=14, fill='black', font_family=font_name, text_anchor="start", alignment_baseline="middle")
    name = dwg.text("Antonio Kim", insert=(20, height_mm * 0.5 + 20), font_size=12, fill='black', font_family=font_name, text_anchor="start", alignment_baseline="middle")
    title = dwg.text("Master", insert=(20, height_mm * 0.5 + 40), font_size=10, fill='black', font_family=font_name, text_anchor="start", alignment_baseline="middle")

    dwg.add(company)
    dwg.add(name)
    dwg.add(title)
    dwg.save()

async def svg_to_pdf(input_svg, output_pdf):
    browser = await launch()
    page = await browser.newPage()

    await page.setViewport({"width": 1280, "height": 1024})
    await page.setContent(f"<html><body>{input_svg}</body></html>")

    await page.pdf({"path": output_pdf, 'format': 'A5', 'printBackground': True})

    await browser.close()

def merge_pages(front_page, back_page):
    # merged_page = PyPDF2.PageObject.createBlankPage(None, front_page.mediaBox.getWidth() * 2, front_page.mediaBox.getHeight())
    # merged_page.merge_page(front_page)
    # merged_page.mergeTranslatedPage(back_page, front_page.mediaBox.getUpperRight_x(), 0)
    # return merged_page
    if not front_page or not back_page:
        raise ValueError("Invalid input: front_page or back_page is None")

    width = front_page.mediabox.upper_right[0] - front_page.mediabox.lower_left[0]
    height = front_page.mediabox.upper_right[1] - front_page.mediabox.lower_left[1]
    merged_page = PyPDF2.PageObject.create_blank_page(None, width * 2, height)
    merged_page.merge_page(front_page)
    back_page.add_transformation(PyPDF2.Transformation().translate(width, 0))
    merged_page.merge_page(back_page)

    return merged_page

async def main():
    font_path = 'font/NanumBarunGothic.ttf'
    font_name = 'NanumBarunGothic'

    width_mm = 90
    height_mm = 50
    width = f"{width_mm}mm"
    height = f"{height_mm}mm"

    # SVG 파일 생성
    front_card = 'front_card.svg'
    back_card = 'back_card.svg'
    create_front_card_svg(front_card, width, height, font_path, font_name)
    create_back_card_svg(back_card, width, height, font_path, font_name, height_mm)


    # 각각의 SVG 파일을 PDF로 변환
    pdf_front_card = 'front_card.pdf'
    pdf_back_card = 'back_card.pdf'

    with open(front_card, 'r', encoding='utf-8') as file:
        front_svg_content = file.read()

    with open(back_card, 'r', encoding='utf-8') as file:
        back_svg_content = file.read()

    await svg_to_pdf(front_svg_content, pdf_front_card)
    await svg_to_pdf(back_svg_content, pdf_back_card)

    # PDF 파일 병합
    output_pdf = 'combined_cards.pdf'
    pdf_writer = PyPDF2.PdfWriter()

    front_pdf = PyPDF2.PdfReader(pdf_front_card)
    back_pdf = PyPDF2.PdfReader(pdf_back_card)

    front_page = front_pdf.pages[0]
    back_page = back_pdf.pages[0]

    # 두 명함 이미지를 한 페이지에 나란히 배치
    merged_page = merge_pages(front_page, back_page)

    pdf_writer.add_page(merged_page)

    with open(output_pdf, 'wb') as out_file:
        pdf_writer.write(out_file)

    # front_pdf = PdfReader(pdf_front_card)
    # back_pdf = PdfReader(pdf_back_card)

    # front_page = front_pdf.pages[0]
    # back_page = back_pdf.pages[0]

    # # 두 명함 이미지를 한 페이지에 배치
    # # front_page.merge_page(back_page)

    # # pdf_writer.add_page(front_page)
    # # pdf_writer.add_page(back_page)

    # merged_page = merge_pages(front_page, back_page)

    # pdf_writer.add_page(merged_page)

    # with open(output_pdf, 'wb') as out_file:
    #     pdf_writer.write(out_file)

if __name__ == "__main__":
    asyncio.run(main())