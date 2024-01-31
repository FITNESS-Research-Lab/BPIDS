import xml.etree.ElementTree as ET
import json

# Step 1: Parse BPMN XML File
def parse_bpmn_tasks(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tasks = []

        for process in root.findall('{http://www.omg.org/spec/BPMN/20100524/MODEL}process'):
            for task in process.findall('{http://www.omg.org/spec/BPMN/20100524/MODEL}scriptTask'):
                tasks.append(task.attrib['name'])

        return tasks
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except FileNotFoundError:
        print(f"File not found: {xml_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return []

# Function to request input with validation
def request_input(prompt, validation=lambda x: True, error_message="Invalid input, please try again."):
    while True:
        user_input = input(prompt)
        if validation(user_input):
            return user_input
        else:
            print(error_message)

# Function to request integer input
def request_integer_input(prompt):
    return request_input(
        prompt,
        lambda x: x.isdigit(),
        "The input must be an integer. Please try again."
    )

# Step 3: FSM Creation
def create_fsm_for_task(task_id):
    print(f"\nCreating FSM for Task: {task_id}")
    fsm_name = request_input("Please insert the name of the FSM: ")

    num_states = int(request_integer_input("Enter the number of states, initial state excluded: "))
    initial_state = request_input("Enter the initial state name: ")
    states = [request_input(f"Enter state {i+1} name: ") for i in range(num_states)]
    states.insert(0, initial_state)

    transitions = []
    while True:
        add_transition = request_input("Do you want to add a transition? (yes/no): ", lambda x: x in ['yes', 'no']).lower()
        if add_transition != 'yes':
            break

        source = request_input("Enter the source state: ", lambda x: x in states, "State does not exist. Please enter a valid state.")
        target = request_input("Enter the target state: ", lambda x: x in states, "State does not exist. Please enter a valid state.")
        condition = input("Enter a condition (or leave blank for no condition): ")

        transitions.append({'source': source, 'target': target, 'condition': condition})

    fsm_structure = {
        'name': fsm_name,
        'initial_state': initial_state,
        'states': states,
        'transitions': transitions
    }

    with open(f"{fsm_name}_fsm_structure.json", "w") as file:
        json.dump(fsm_structure, file, indent=4)

    print(f"FSM structure saved to {fsm_name}_fsm_structure.json")

# Main program
def main():
    bpmn_file = request_input("Enter the path to the BPMN XML file: ")
    tasks = parse_bpmn_tasks(bpmn_file)

    for task in tasks:
        print(f"\nTask found: {task}")
        create_fsm = request_input(f"Do you want to create an FSM for '{task}'? (yes/no): ", lambda x: x in ['yes', 'no']).lower()
        if create_fsm == 'yes':
            create_fsm_for_task(task)

if __name__ == "__main__":
    main()
