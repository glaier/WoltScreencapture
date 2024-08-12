# WoltScreencapture
Python scripts to capture info on earnings
#Installing needed packages 

sudo dnf install tesseract tesseract-langpack-dan
tesseract --list-langs
find /usr/share/ -type d -name "tessdata"
export TESSDATA_PREFIX=/usr/share/tesseract/

You can add this line to your ~/.bashrc or ~/.bash_profile to set it permanently.

#OCRtoTXT script
Process png screen capture files with info on Wolt Partner earnings
Use OCR to txt

#TXTtoCSV script
Convert txt from OCR processing to CSV file

##Options
-d remove duplicates
-O output file
-P input directory with txt files

python TXTtoCSV.py -P /home/gunnarhellmundlaier/Downloads/txt_files -O deliveries.csv -d
