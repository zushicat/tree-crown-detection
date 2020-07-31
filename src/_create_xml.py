import re
from typing import Any, Dict

from bs4 import BeautifulSoup


def prettify(self, encoding=None, formatter="minimal", indent_width=4):
    return r.sub(r'\1' * indent_width, orig_prettify(self, encoding, formatter))


orig_prettify = BeautifulSoup.prettify
r = re.compile(r'^(\s*)', re.MULTILINE)
BeautifulSoup.prettify = prettify
"""
hack for better prettyprint
https://stackoverflow.com/questions/15509397/custom-indent-width-for-beautifulsoup-prettify
"""


def _get_base_html() -> Any:
    doc = '''
            <annotation>
                <folder></folder>
                <filename></filename>
                <path></path>
                <source>
                    <database>Unknown</database>
                </source>
                <size>
                    <width></width>
                    <height></height>
                    <depth>3</depth>
                </size>
                <segmented>0</segmented>
            </annotation>
          '''
    return BeautifulSoup(doc, 'xml')


def _get_box_base_xml() -> Any:
    doc = '''
            <object>
                <pose>Unspecified</pose>
                <truncated>0</truncated>
                <difficult>0</difficult>
                <bndbox>
                    <xmin></xmin>
                    <ymin></ymin>
                    <xmax></xmax>
                    <ymax></ymax>
                </bndbox>
            </object>
          '''
    return BeautifulSoup(doc, 'xml')


def _get_xml_one_line_str(xml: BeautifulSoup) -> str:
    xml_str = str(xml).replace("\t", "").replace("\n", "")
    xml_str = xml_str.replace('<?xml version="1.0" encoding="utf-8"?>', '')
    xml_str = "".join(xml_str.split(" "))
    
    return xml_str


def create_label_xml(groundtruth: Dict[str, Any]) -> str:
    xml = _get_base_html()
    xml.annotation.folder.string = groundtruth["folder"]
    xml.annotation.filename.string = groundtruth["filename"]
    xml.annotation.path.string = groundtruth["path"]
    xml.annotation.size.width.string = str(groundtruth["width"])
    xml.annotation.size.height.string = str(groundtruth["height"])

    for box in groundtruth["label_boxes"]:
        box_xml = _get_box_base_xml()
        name_tag = BeautifulSoup(f"<name>{box['label']}</name>", 'xml')
        box_xml.object.append(name_tag)

        xmin = int(box["xmin"])
        ymin = int(box["ymin"])
        xmax = int(box["xmax"])
        ymax = int(box["ymax"])

        box_xml.object.bndbox.xmin.string = str(xmin)
        box_xml.object.bndbox.ymin.string = str(ymin)
        box_xml.object.bndbox.xmax.string = str(xmax)
        box_xml.object.bndbox.ymax.string = str(ymax)

        xml.annotation.append(box_xml)

    xml_str: str = _get_xml_one_line_str(xml)

    return xml_str
