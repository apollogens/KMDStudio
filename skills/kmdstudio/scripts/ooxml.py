"""Namespaces and the deliberately small OPC package profile."""

import xml.etree.ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
XML = "http://www.w3.org/XML/1998/namespace"
MIME = "application/vnd.openxmlformats-officedocument."

NS = dict(w=W, r=R, wp=WP, a=A, pic=PIC, rel=REL, ct=CT, cp=CP, dc=DC, xml=XML)
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

MAIN_PARTS = {
    "/word/document.xml": MIME + "wordprocessingml.document.main+xml",
    "/word/styles.xml": MIME + "wordprocessingml.styles+xml",
    "/word/numbering.xml": MIME + "wordprocessingml.numbering+xml",
    "/word/footer1.xml": MIME + "wordprocessingml.footer+xml",
    "/docProps/core.xml": "application/vnd.openxmlformats-package.core-properties+xml",
}
ROOT_RELS = [
    ("rIdDocument", R + "/officeDocument", "word/document.xml"),
    ("rIdCore", REL + "/metadata/core-properties", "docProps/core.xml"),
]
MAIN_RELS = [
    ("rIdStyles", R + "/styles", "styles.xml"),
    ("rIdNumbering", R + "/numbering", "numbering.xml"),
    ("rIdFooter", R + "/footer", "footer1.xml"),
]


def q(name):
    prefix, local = name.split(":", 1)
    return f"{{{NS[prefix]}}}{local}"


def element(tag, parent=None, text=None, **attrs):
    attrs = {q(k.replace("_", ":", 1)) if "_" in k else k: str(v)
             for k, v in attrs.items()}
    node = ET.Element(q(tag), attrs) if parent is None else ET.SubElement(parent, q(tag), attrs)
    node.text = text
    return node


def w(tag, parent=None, **attrs):
    return element("w:" + tag, parent, **{"w_" + key: value for key, value in attrs.items()})


def val(name, parent, value):
    return w(name, parent, val=value)


def relationships(records):
    # Writer's package type detection expects unprefixed OPC metadata tags.
    root = ET.Element("Relationships", xmlns=REL)
    for identity, kind, target in records:
        ET.SubElement(root, "Relationship", Id=identity, Type=kind, Target=target)
    return root


def content_types(header, images):
    root = ET.Element("Types", xmlns=CT)
    defaults = {
        "rels": "application/vnd.openxmlformats-package.relationships+xml",
        "xml": "application/xml",
    }
    if images:
        defaults["png"] = "image/png"
    for suffix, kind in defaults.items():
        ET.SubElement(root, "Default", Extension=suffix, ContentType=kind)
    for name, kind in MAIN_PARTS.items():
        ET.SubElement(root, "Override", PartName=name, ContentType=kind)
    if header:
        ET.SubElement(root, "Override", PartName="/word/header1.xml",
                      ContentType=MIME + "wordprocessingml.header+xml")
    return root
