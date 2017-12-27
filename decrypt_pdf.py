from PyPDF2 import PdfFileReader, PdfFileWriter

class DecryptPDF:
    def decrypt(input_path, output_path, password):
        with open(input_path, 'rb') as input_file, \
            open(output_path, 'wb') as output_file:
            reader = PdfFileReader(input_file)
            res = reader.decrypt(password)
            writer = PdfFileWriter()

            for i in range(reader.getNumPages()):
                writer.addPage(reader.getPage(i))
            
            writer.write(output_file)
            return res
