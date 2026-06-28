FROM python:3.12-slim

WORKDIR /workspace

RUN pip install --no-cache-dir pypdf==5.1.0

COPY extract_pdf.py /usr/local/bin/extract_pdf.py

ENTRYPOINT ["python", "/usr/local/bin/extract_pdf.py"]
