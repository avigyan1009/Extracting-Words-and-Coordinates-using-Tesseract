import pytesseract
import io
from lxml import etree
import cv2
    
def get_hocr_output(image_path):
    """
    extract text and metadata from uploaded image
    uploaded_file : in-memory image
    """
    image = cv2.imread(image_path)
    xml_bytes_object = pytesseract.image_to_pdf_or_hocr(image, extension="hocr")
    text_and_metadata_list = text_extraction_from_xml(xml_bytes_object)
    json_metadata = create_metadata_json(text_and_metadata_list)
    return json_metadata


def text_extraction_from_xml(xml_bytes_object):
    """
    manipulate xml and extract text from xml
    xml_bytes_object : ouput of hocr
    """
    doc = etree.parse(io.BytesIO(xml_bytes_object))
    consolidate_list = []
    for index,path in enumerate(doc.xpath('//*')):
        if 'ocrx_word' in path.values() :
            conf = [x for x in path.values() if 'x_wconf' in x][0]
            conf_value = int(conf.split('x_wconf ')[1])
            coor = [x for x in path.values() if 'bbox' in x][0]
            coor_value = coor.split(";")[0].split(" ")[1:]
            if path.text == None:
                text = doc.xpath("//*")[index+1].text
            else:
                text = path.text
            if text != None and text !=" " :
                consolidate_list.append((conf_value,text,coor_value))
    token_list = []
    for _ in consolidate_list:
        item = []
        for i in _:
            if isinstance(i,list): item.extend(i)
            else: item.append(i)
        token_list.append(item)
    return token_list

def create_metadata_json(token_list):
    """
    manipulate text and metadata list into json
    token_list : list of token and metadata
    """
    layout = {}
    layout["docstructure"]=[]
    layout["metadata"] = []    
    
    for index, meta_data in enumerate(token_list):
        if len(meta_data)>1:
            text = ""
            if index !=0 and len(meta_data)>6:
                    text = "".join(meta_data[1:-4])
                    layout["docstructure"].append(text.strip())
                    layout["metadata"].append({
                                            "text" : text.strip(),
                                            "y1" : int(meta_data[-3].strip()) 
                                                if len(meta_data[-3])>0 and meta_data[-3].strip().isdigit() else 0,
                                            "y2" : int(meta_data[-1].strip())
                                                if len(meta_data[-1])>0 and meta_data[-1].strip().isdigit() else 0,
                                            "x1" : int(meta_data[-4].strip())
                                                if len(meta_data[-4])>0 and meta_data[-4].strip().isdigit() else 0,
                                            "x2" : int(meta_data[-2].strip())
                                                if len(meta_data[-2])>0 and meta_data[-2].strip().isdigit()  else 0,
                                            "height" : 0,
                                            "width" : 0
                                        })
                    
            else:
                layout["docstructure"].append(meta_data[1].strip())
                layout["metadata"].append({
                                            "text" : meta_data[1].strip(),
                                            "y1" : int(meta_data[3].strip()) 
                                                if len(meta_data[3])>0 and meta_data[3].strip().isdigit() else 0,
                                            "y2" : int(meta_data[5].strip())
                                                if len(meta_data[5])>0 and meta_data[5].strip().isdigit() else 0,
                                            "x1" : int(meta_data[2].strip())
                                                if len(meta_data[2])>0 and meta_data[2].strip().isdigit() else 0,
                                            "x2" : int(meta_data[4].strip())
                                                if len(meta_data[4])>0 and meta_data[4].strip().isdigit()  else 0,
                                            "height" : int(meta_data[5].strip()) - int(meta_data[3].strip()) 
                                                if len(meta_data[5])>0 and len(meta_data[3])>0 and meta_data[5].strip().isdigit() and meta_data[3].strip().isdigit() else 0,
                                            "width" : int(meta_data[4].strip()) - int(meta_data[2].strip())
                                                if len(meta_data[4])>0 and len(meta_data[2])>0  and meta_data[4].strip().isdigit() and meta_data[2].strip().isdigit() else 0,
                                            })
    return layout
    



