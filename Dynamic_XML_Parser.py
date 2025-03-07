import os
import re
import xml.etree.ElementTree as ET
from copy import deepcopy

def split_syteline_objects(
    input_xml_path,
    base_output_directory,
    items_to_extract=None
):
    """
    Splits a large SyteLine XML (AllCustomizedObjects.xml) into separate XML files
    for each item type.

    items_to_extract: A dictionary that maps the singular item tag to its plural container tag.
      For example:
        {
           "Form": "Forms",
           "ComponentClass": "ComponentClasses",
           "PropertyClassExtension": "PropertyClassExtensions",
           "WebUserControl": "WebUserControls",
           "Explorer": "Explorers",
           "Script": "Scripts",
           "String": "Strings",
           "Validator": "Validators",
           "Variable": "Variables",
           "Theme": "Themes"
        }

    For each item type, we create an output subdirectory named:
      "Bulk Customization {item_tag} Export"
    inside the specified base_output_directory.

    In each container (e.g. <Forms>), we look for <Form ...>, copy each into a new minimal XML,
    and name each output file by the item's Name attribute, e.g. "AccountsPayableAgingReportViewer.xml".

    Note: We parse the large XML once, then iterate over the specified item types.
          If a container doesn't exist, we skip it.
    """

    if items_to_extract is None:
        items_to_extract = {}

    # Parse the entire XML one time
    tree = ET.parse(input_xml_path)
    root = tree.getroot()

    # The top-level element and attributes, e.g. <FormsAndObjectsExport Version="...">
    top_level_tag = root.tag
    top_level_attrib = dict(root.attrib)

    # Ensure the base output directory exists
    os.makedirs(base_output_directory, exist_ok=True)

    # For each item type, find the corresponding container
    for item_tag, container_tag in items_to_extract.items():
        # Attempt to locate the container element in the root
        container_element = root.find(container_tag)
        if container_element is None:
            print(f"No <{container_tag}> element found for item '{item_tag}'. Skipping.")
            continue

        # List all item elements, e.g. <Form>, <ComponentClass>, etc.
        items = container_element.findall(item_tag)
        if not items:
            print(f"No <{item_tag}> elements found inside <{container_tag}>. Skipping.")
            continue

        # Create a subdirectory for this item type, e.g. 
        #   Bulk Customization Export\Bulk Customization Form Export
        subdirectory_name = f"{container_tag}"
        output_directory = os.path.join(base_output_directory, subdirectory_name)
        os.makedirs(output_directory, exist_ok=True)

        # Container attributes, e.g. "Type" for <Forms Type="1">
        container_attrib = dict(container_element.attrib)

        # For each <item_tag ... Name="XYZ">, create a separate file
        for item in items:
            item_name = item.attrib.get("Name", "UnnamedItem")

            # 1) Sanitize item_name to remove or replace invalid filename chars.
            safe_item_name = re.sub(r'[\\/*?:"<>|]', '_', item_name)

            # 2) Create the new minimal XML structure
            new_root = ET.Element(top_level_tag, top_level_attrib)
            new_container = ET.SubElement(new_root, container_tag, container_attrib)
            new_container.append(deepcopy(item))

            # 3) Create the output path, now using `safe_item_name`
            output_file_path = os.path.join(output_directory, f"{safe_item_name}.xml")

            new_tree = ET.ElementTree(new_root)
            new_tree.write(output_file_path, xml_declaration=True, encoding="utf-8")
            print(f"Created: {output_file_path}")


if __name__ == "__main__":

    # The input XML path (the file that contains all the objects you want to split)
    input_file = r"G:\CSI10\FormScripts (XML)\AllCustomizedObjects.xml"

    # Base output directory (everything goes in subfolders under here)
    base_output_dir = r"G:\CSI10\FormScripts (XML)\Bulk Customization Export"

    # This dictionary maps singular item tags to the plural container tags
    # used by SyteLine. (Adjust if your XML uses different tag names.)
    items_map = {
        # "ItemTag": "ContainerTag"
        "Form": "Forms",
        "ComponentClass": "ComponentClasses",
        "PropertyClassExtension": "PropertyClassExtensions",
        "WebUserControl": "WebUserControls",
        "Explorer": "Explorers",
        "Script": "Scripts",
        "String": "Strings",
        "Validator": "Validators",
        "Variable": "Variables",
        "Theme": "Themes",
    }

    # Call the splitting function
    split_syteline_objects(
        input_xml_path=input_file,
        base_output_directory=base_output_dir,
        items_to_extract=items_map
    )
