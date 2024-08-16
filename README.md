# WoltScreencapture
Python scripts to capture info on earnings<br>

#Installing needed packages 

sudo dnf install tesseract tesseract-langpack-dan<br>
tesseract --list-langs<br>
find /usr/share/ -type d -name "tessdata"<br>
export TESSDATA_PREFIX=/usr/share/tesseract/<br>
<br>
You can add this line to your ~/.bashrc or ~/.bash_profile to set it permanently.<br>

#OCRtoTXT script
Process png screen capture files with info on Wolt Partner earnings<br>
Use OCR to txt<br>

#TXTtoCSV script
Convert txt from OCR processing to CSV file<br>

##Options
-d remove duplicates<br>
-O output file<br>
-P input directory with txt files<br>

python TXTtoCSV.py -P /home/gunnarhellmundlaier/Downloads/txt_files -O deliveries.csv -d<br>
