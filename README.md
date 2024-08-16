# WoltScreencapture
Python scripts to capture info on earnings<br>

# Installing needed packages 
```sudo dnf install tesseract tesseract-langpack-dan
tesseract --list-langs
find /usr/share/ -type d -name "tessdata"
export TESSDATA_PREFIX=/usr/share/tesseract/```<br>
<br>
You can add this line to your ~/.bashrc or ~/.bash_profile to set it permanently.<br>
<br>
```pip install pillow```<br>


# stich_images script
Concatenate PNG files and prepare for OCR.<br>
```python stitch_images.py image1.png image2.png image3.png```<br>
<br>
or <br>
<br>
```python stitch_images.py /path/to/folder```<br>


# OCRtoTXT script
Process png screen capture files with info on Wolt Partner earnings<br>
Use OCR to txt<br>

# TXTtoCSV script
Convert txt from OCR processing to CSV file<br>

## Options
-d remove duplicates<br>
-O output file<br>
-P input directory with txt files<br>
<br>
python TXTtoCSV.py -P /home/gunnarhellmundlaier/Downloads/txt_files -O deliveries.csv -d<br>
