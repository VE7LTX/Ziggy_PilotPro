# ==========================================================
#                 File Inspector Tool
# ==========================================================
# 
# Overview:
# This Python script inspects Python files in the main directory and extracts 
# information about their components. It identifies imports, comments, classes, 
# functions, variables, and control flow elements, and then lists them in a 
# hierarchical tree structure in an output file.
#
# Features:
# 1. Parses and analyzes Python files using the Abstract Syntax Trees (AST).
# 2. Recognizes and lists various Python components along with their line numbers.
# 3. Generates an organized tree structure of the components in the main directory.
# 4. Provides options to ignore specific folders and files.
# 5. Outputs the tree structure to a user-defined file for further inspection.
#
# Usage:
# Run this script directly to inspect Python files in the current directory. The 
# results will be saved to the default output file "file_tree_with_components.txt".
#
# Dependencies:
# - Python's AST module for code inspection.
# - Python's os module for directory navigation.
#
# Author:
# Matthew Schafer
# Last Updated: Aug 31, 2023
# ==========================================================

import os
import ast
import tokenize
import io
from typing import List

OUTPUT_FILE_NAME = "file_tree_with_components.txt"
IGNORED_FOLDERS = [".vscode", "OLD", "build", "__mypycache__"]

def extract_calls(node: ast.AST) -> List[str]:
    """
    Extracts function and method calls from a given AST node.

    Args:
    - node (ast.AST): The AST node to extract calls from.

    Returns:
    - List[str]: A list containing the function and method calls.
    """
    calls = []

    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                # Function call
                calls.append(f"Line {n.lineno}: Call to function: {n.func.id}")
            elif isinstance(n.func, ast.Attribute):
                # Method call or attribute access
                object_name = n.func.value.id if isinstance(n.func.value, ast.Name) else "<complex_expression>"
                calls.append(f"Line {n.lineno}: Call to method: {n.func.attr} of object {object_name}")


    return calls

def extract_python_components(file_path: str) -> List[str]:
    """
    Extracts imports, comments, classes, functions, variables, and control flow elements from a Python file.
    It also returns the line number for each component.
    
    Args:
    - file_path (str): The path to the Python file.
    
    Returns:
    - List[str]: A list containing the components of the Python file in their appearing order.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        source = file.read()
        tree = ast.parse(source)

    components = []

    # Extract comments from the source
    comments = [f"Line {token[2][0]}: # {token[1]}" for token in tokenize.tokenize(io.BytesIO(source.encode('utf-8')).readline) if token.type == tokenize.COMMENT]
    components.extend(comments)

    # Helper function to extract line number
    def get_line_number(component: str) -> int:
        return int(component.split("Line")[1].split(":")[0].strip())

    # Add imports
    for node in tree.body:
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            components.append(f"Line {node.lineno}: Import: {ast.dump(node)}")

    # Helper function to extract control flows
    def extract_control_flows(node, indent=0) -> List[str]:
        inner_components = []

        # Ensure the node has a 'body' attribute before processing
        if not hasattr(node, 'body'):
            return inner_components

        for inner_node in node.body:
            if isinstance(inner_node, ast.If):
                inner_components.append(f"Line {inner_node.lineno}:" + ' ' * indent + "If statement")
                inner_components += extract_control_flows(inner_node, indent + 2)
                if inner_node.orelse:
                    for else_node in inner_node.orelse:
                        if isinstance(else_node, ast.If):  # Handle "elif" blocks
                            inner_components.append(f"Line {else_node.lineno}:" + ' ' * indent + "Elif statement")
                        else:
                            inner_components.append(f"Line {inner_node.orelse[0].lineno}:" + ' ' * indent + "Else statement")
                        inner_components += extract_control_flows(else_node, indent + 2)
            elif isinstance(inner_node, ast.For):
                inner_components.append(f"Line {inner_node.lineno}:" + ' ' * indent + "For loop")
                inner_components += extract_control_flows(inner_node, indent + 2)
            elif isinstance(inner_node, ast.While):
                inner_components.append(f"Line {inner_node.lineno}:" + ' ' * indent + "While loop")
                inner_components += extract_control_flows(inner_node, indent + 2)
            elif isinstance(inner_node, ast.Assign):
                for target in inner_node.targets:
                    if isinstance(target, ast.Name):
                        inner_components.append(f"Line {inner_node.lineno}:" + ' ' * indent + f"Variable: {target.id}")
        return inner_components

    # Add other components
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            components.append(f"Line {node.lineno}: Function: {node.name}")
            components += extract_control_flows(node)
        elif isinstance(node, ast.ClassDef):
            components.append(f"Line {node.lineno}: Class: {node.name}")
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    components.append(f"Line {class_node.lineno}:  Function: {class_node.name}")
                    components += extract_control_flows(class_node, 2)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    components.append(f"Line {node.lineno}: Variable: {target.id}")

    # Add function and method calls
    calls = extract_calls(tree)
    components.extend(calls)

    # Sort the components based on line numbers for proper ordering
    components.sort(key=get_line_number)

    return components



def list_files_and_components_in_main_directory(directory: str) -> List[str]:
    """
    Lists all files and their Python components in the main directory.
    
    Args:
    - directory (str): The directory path to search.
    
    Returns:
    - List[str]: A list containing the file tree and components of the main directory.
    """
    tree = []

    for item in os.listdir(directory):
        if item not in IGNORED_FOLDERS and item.endswith(".py"):
            item_path = os.path.join(directory, item)
            tree.append(f"{item}\n")
            tree += extract_python_components(item_path)
            tree.append("\n\n")

    return tree

def save_tree_to_file(directory: str, output_file: str = OUTPUT_FILE_NAME) -> None:
    """
    Lists all files and their Python components in the main directory and saves them to a file.
    
    Args:
    - directory (str): The directory path to search.
    - output_file (str): The name of the output file where the tree will be saved.
    """
    tree = list_files_and_components_in_main_directory(directory)

    with open(output_file, "w") as file:
        file.write("\n".join(tree))


if __name__ == "__main__":
    current_directory = os.getcwd()
    save_tree_to_file(current_directory)
    print(f"File tree with components saved to {OUTPUT_FILE_NAME}")

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# End of File Inspector Tool.
#
# Purpose:
# This tool aids developers in understanding the structure and components 
# of Python files in the main directory. By generating a clear tree structure,
# it helps in reviewing code, ensuring consistency, and facilitating maintenance.
#
# Future Enhancements:
# 1. Extend the tool to traverse subdirectories.
# 2. Provide a user interface for easier configuration and navigation.
# 3. Enhance the formatting of the output for improved readability.
# 4. Integrate with version control systems to track file changes over time.
#
# Note: Always review and test the tool after making modifications to ensure its accuracy and reliability.
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
