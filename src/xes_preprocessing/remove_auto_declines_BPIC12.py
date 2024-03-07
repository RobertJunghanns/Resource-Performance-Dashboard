import xml.etree.ElementTree as ET
import re

def remove_namespaces(xml_string):
    """
    Removes namespaces from an XML string.
    
    Parameters:
    - xml_string: The XML content as a string.
    
    Returns:
    - The XML string with namespaces removed.
    """
    return re.sub(r'\sxmlns(:ns0)?="[^"]+"', '', xml_string)

def filter_traces_and_remove_namespace(file_path, output_file_path, min_events=4):
    """
    Filters out traces with three or fewer events from an XES log file and removes namespaces.
    
    Parameters:
    - file_path: Path to the XES log file.
    - output_file_path: Path for the output XES log file without namespaces.
    - min_events: Minimum number of events a trace must have to be retained.
    """
    # Parse the XES log file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace handling is implicit in the elements' removal
    trace_tag = 'trace'
    event_tag = 'event'

    # Iterate over all traces in the log
    traces_to_remove = []
    for trace in root.findall('.//'+trace_tag):
        events = trace.findall('.//'+event_tag)
        # If the trace has three or fewer events, mark it for removal
        if len(events) <= min_events - 1:
            traces_to_remove.append(trace)

    # Remove the marked traces
    for trace in traces_to_remove:
        root.remove(trace)

    # Convert the tree to a string and remove namespaces
    xml_string = ET.tostring(root, encoding='unicode')
    cleaned_xml_string = remove_namespaces(xml_string)

    # Save the modified, namespace-free XML to a new file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(cleaned_xml_string)

# Example usage
input_file_path = './src/data/BPI_Challenge_2012.xes'
output_file_path = './src/data/BPI_Challenge_2012_no_auto_declines.xes'
filter_traces_and_remove_namespace(input_file_path, output_file_path)