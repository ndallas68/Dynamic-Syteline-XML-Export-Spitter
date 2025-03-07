import os
import xml.etree.ElementTree as ET
from copy import deepcopy

def split_syteline_xml(
    input_xml_path,
    output_directory,
    container_tag,
    item_tag,
    filename_attribute="Name"
):
    """
    Generic XML splitting function for CSI/Syteline exports.
    
    1. Parses the top-level XML document (e.g., <FormsAndObjectsExport>).
    2. Finds the container element (e.g., <Forms>) by `container_tag`.
    3. Iterates over each child element (e.g., <Form>) by `item_tag`.
    4. For each item, creates a new XML file containing:
       - A copy of the original top-level element (with the same name and attributes).
       - A single container element (with the same `container_tag` and attributes).
       - A deep-copied child item (e.g. <Form>).
    5. Names the output file using the item’s `filename_attribute` (default = "Name"), 
       falling back to "UnnamedItem.xml" if that attribute does not exist.

    :param input_xml_path:     Full path to the large input XML file.
    :param output_directory:   Directory where individual .xml files will be saved.
    :param container_tag:      XML tag of the container element (e.g. "Forms", "Strings").
    :param item_tag:           XML tag of the child elements to extract (e.g. "Form", "String").
    :param filename_attribute: Name of the attribute to use for each item's output filename.
    """

    # Parse the full XML
    tree = ET.parse(input_xml_path)
    root = tree.getroot()
    
    # Keep the top-level element name and all its attributes exactly as in the original.
    # e.g. <FormsAndObjectsExport Version="010000">
    top_level_tag = root.tag
    top_level_attrib = dict(root.attrib)

    # Find the container element we want to split on, e.g. <Forms Type="1">
    container_element = root.find(container_tag)
    if container_element is None:
        print(f"No <{container_tag}> element found. Exiting.")
        return

    # Keep the container's attributes (e.g. {"Type": "1"})
    container_attrib = dict(container_element.attrib)

    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Go through each item in the container
    items = container_element.findall(item_tag)
    if not items:
        print(f"No <{item_tag}> elements found inside <{container_tag}>. Exiting.")
        return

    for item in items:
        # Grab the attribute we want to use for the filename
        item_name = item.attrib.get(filename_attribute, "UnnamedItem")

        # Create a new top-level root (same tag & attributes as the original)
        new_root = ET.Element(top_level_tag, top_level_attrib)

        # Create the sub-element for the container (same tag & attributes)
        new_container = ET.SubElement(new_root, container_tag, container_attrib)

        # Deep copy the item (so we don't remove it from the original tree)
        new_container.append(deepcopy(item))

        # Convert to an ElementTree
        new_tree = ET.ElementTree(new_root)

        # Construct an output path like "G:\OutputDir\ItemName.xml"
        out_file_path = os.path.join(output_directory, f"{item_name}.xml")

        # Write with XML declaration, UTF-8 encoding
        new_tree.write(out_file_path, xml_declaration=True, encoding="utf-8")
        print(f"Created: {out_file_path}")


if __name__ == "__main__":
    # EXAMPLE USAGE #1: Splitting forms
    # ---------------------------------------------------------
    input_file = r"G:\CSI10\FormScripts (XML)\AllCustomizedForms.xml"
    output_dir = r"G:\CSI10\FormScripts (XML)\Bulk Customization Export"

    # For Syteline form exports, the container tag is "Forms" and the items are "Form",
    # typically named with a "Name" attribute.
    split_syteline_xml(
        input_xml_path=input_file,
        output_directory=output_dir,
        container_tag="Forms",
        item_tag="Form",
        filename_attribute="Name"
    )

    # EXAMPLE USAGE #2: Splitting strings or translations
    # ---------------------------------------------------------
    # Suppose your file has <FormsAndObjectsExport ...><Strings>...</Strings></FormsAndObjectsExport>
    # with individual <String Name="...">. Then you could do:
    # split_syteline_xml(
    #     input_xml_path=r"path\to\AllCustomizedStrings.xml",
    #     output_directory=r"path\to\strings\output",
    #     container_tag="Strings",
    #     item_tag="String",
    #     filename_attribute="Name"
    # )
