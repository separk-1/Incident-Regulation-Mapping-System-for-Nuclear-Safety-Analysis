import os
import re
import pdfplumber
from tqdm import tqdm

RAW_LER_DIR = "../../data/raw/ler"
OUTPUT_TEXT_DIR = "../../data/processed/ler_text"

os.makedirs(OUTPUT_TEXT_DIR, exist_ok=True)

def process_all_pdfs(raw_dir, output_dir):
    pdf_files = [f for f in os.listdir(raw_dir) if f.lower().endswith(".pdf")]

    for pdf_file in tqdm(pdf_files, desc="Processing LER PDFs", unit="file"):
        pdf_path = os.path.join(raw_dir, pdf_file)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                start_page = None
                # 각 페이지 텍스트를 추출하면서 LICENSEE EVENT REPORT (LER) 존재여부 확인
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    # "LICENSEE EVENT REPORT (LER)"를 포함하는지 검사
                    if "LICENSEE EVENT REPORT (LER)" in text.upper():
                        start_page = idx
                        break

                if start_page is None:
                    # 해당 PDF에서 LER 페이지 찾지 못함 → 빈 텍스트 또는 Not Found 처리
                    extracted_text = "LICENSEE EVENT REPORT (LER) not found."
                else:
                    # start_page부터 끝 페이지까지 텍스트 추출 후 합치기
                    extracted_texts = []
                    for p_idx in range(start_page, len(pdf.pages)):
                        p_text = pdf.pages[p_idx].extract_text() or ""
                        extracted_texts.append(p_text)
                    extracted_text = "\n".join(extracted_texts)

                # 텍스트 파일로 저장
                txt_filename = os.path.splitext(pdf_file)[0] + ".txt"
                txt_path = os.path.join(output_dir, txt_filename)
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text)

        except Exception as e:
            # PDF 처리 중 에러 발생 시 로그 출력 및 빈 파일 생성
            print(f"Error processing {pdf_file}: {e}")
            txt_filename = os.path.splitext(pdf_file)[0] + ".txt"
            txt_path = os.path.join(output_dir, txt_filename)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("Error extracting text.")

# 실행
process_all_pdfs(RAW_LER_DIR, OUTPUT_TEXT_DIR)
