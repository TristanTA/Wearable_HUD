from agent_ui.test_data import test_data_inputs
from agent_ui.input_registry import RegistryManager
from agent_ui.user_input import USER_INPUT
from agent_ui.ui_generator import UIPrompt

def main():
    registry = RegistryManager(test_data_inputs)
    user_input = USER_INPUT

    ui_code = UIPrompt(registry, user_input)
    print(ui_code.get_response())


if __name__ == "__main__":
    main()