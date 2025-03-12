import os
import re
import xml.etree.ElementTree as ET
from copy import deepcopy

# For file dialogs
import tkinter as tk
from tkinter.filedialog import askopenfilename

def get_input_file():
    """
    Pops up a file dialog prompting the user to select the SyteLine export XML.
    Returns the selected file path as a string, or None if user cancels.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = askopenfilename(
        title="Select the SyteLine Export XML",
        filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
    )
    # If the user cancels, file_path will be ""
    return file_path if file_path else None

def split_syteline_objects(
    tree: ET.ElementTree,
    base_output_directory: str,
    items_to_extract: dict
):
    """
    Splits a SyteLine export XML (already parsed as `tree`) into separate XML files
    for each item type.

    :param tree:                 An ElementTree object parsed from the large export file.
    :param base_output_directory:Directory where we create subfolders & write individual XMLs.
    :param items_to_extract:     A dictionary mapping singular item tags -> plural container tags.
                                 Example: {"Form": "Forms", "IDODefinition": "IDODefinitions", ...}
    """

    root = tree.getroot()

    # The top-level element (e.g. <FormsAndObjectsExport ...>) 
    # and its attributes (e.g. {"Version": "010000"})
    top_level_tag = root.tag
    top_level_attrib = dict(root.attrib)

    # Ensure the base output directory exists
    os.makedirs(base_output_directory, exist_ok=True)

    # For each item type, find and process the container tag
    for item_tag, container_tag in items_to_extract.items():
        container_element = root.find(container_tag)
        if container_element is None:
            print(f"No <{container_tag}> element found for item '{item_tag}'. Skipping.")
            continue

        items = container_element.findall(item_tag)
        if not items:
            print(f"No <{item_tag}> elements found inside <{container_tag}>. Skipping.")
            continue

        # Create a subdirectory for this item type
        # e.g. "Bulk Customization Export/Bulk Customization Form Export"
        subdirectory_name = f"{item_tag}"
        output_directory = os.path.join(base_output_directory, subdirectory_name)
        os.makedirs(output_directory, exist_ok=True)

        # Copy attributes from container (like <Forms Type="1">)
        container_attrib = dict(container_element.attrib)

        for item in items:
            item_name = item.attrib.get("Name", "UnnamedItem")

            # If this is an IDODefinition, skip if <AccessAs> is "BaseSyteLine" or "Core"
            if container_tag == "IDODefinitions":
                access_as_el = item.find("AccessAs")
                if access_as_el is not None and access_as_el.text:
                    value = access_as_el.text.strip()
                    if value in {"BaseSyteLine", "Core"}:
                        print(f"Skipping IDO Name='{item_name}' because AccessAs={value}.")
                        continue

            # Replace invalid filename characters with '_'
            safe_item_name = re.sub(r'[\\/*?:"<>|]', '_', item_name)

            # Build a new minimal XML structure
            new_root = ET.Element(top_level_tag, top_level_attrib)
            new_container = ET.SubElement(new_root, container_tag, container_attrib)
            new_container.append(deepcopy(item))

            # Construct the output file path
            output_file_path = os.path.join(output_directory, f"{safe_item_name}.xml")

            # Write out the file
            new_tree = ET.ElementTree(new_root)
            new_tree.write(output_file_path, xml_declaration=True, encoding="utf-8")

            print(f"Created: {output_file_path}")


if __name__ == "__main__":
    # Popup to select the input file
    input_file = get_input_file()
    if not input_file:
        print("No file selected. Exiting.")
        exit(1)

    # The base output directory
    base_output_dir = r"G:\CSI10\FormScripts (XML)\Bulk Customization Export"

    # A dictionary of item-tag -> container-tag
    items_map = {
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
        "IDODefinition": "IDODefinitions"
    }

    # Parse the selected input file
    full_tree = ET.parse(input_file)

    # Split out each object type
    split_syteline_objects(
        tree=full_tree,
        base_output_directory=base_output_dir,
        items_to_extract=items_map
    )
