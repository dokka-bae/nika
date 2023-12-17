from sc_client.client import connect, disconnect, template_search
import logging
from sc_client.constants import sc_types
from sc_client.models import ScTemplate, ScAddr
from sc_kpm.utils import get_system_idtf, get_link_content_data
from sc_kpm import ScKeynodes, ScAgentClassic, ScResult
from sc_kpm.utils.action_utils import (
    create_action_answer,
    finish_action_with_status,
    get_action_arguments,
    get_element_by_role_relation
)
import json

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)

class ConfigSettingsAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_config_settings")
        print('init_suc')

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        print('event_start')
        result = self.processing(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self.logger.info("ConfigSettingsAgent finished %s",
                         "successfully" if is_successful else "unsuccessfully")
        return result

    def processing(self, action_node: ScAddr):
        print("ABOBA")
        current_node_neighbour_list = []
        for i in range(1, 20):
            buffer = self.search_triple_with_role_relation(action_node, ScKeynodes["rrel_" + str(i)])
            if len(buffer) != 0:
                current_node_neighbour_list.append(buffer)
        print(current_node_neighbour_list)
        for i in current_node_neighbour_list:
            print('run')
            self.run(i[1], i[0])
        return ScResult.OK

    def run(self, action_node: ScAddr, number_of_class: int) -> ScResult:
        list_of_example = self.agent(action_node)
        result_list_of_dict = []
        out_names = []
        for i in list_of_example:
            out_names.append(i[0])
            buffer_result = {}
            buffer_dict = {}
            buffer_list = []
            index_of_revers = 0
            counter = 0
            for j in i:
                if j == "__REVERSE":
                    index_of_revers = counter
                else:
                    buffer_dict[str(counter)] = j
                    counter += 1
            for j in range(1, counter):
                if j < index_of_revers:
                    list = [0, j]
                else:
                    list = [j, 0]
                buffer_list.append(list)
            buffer_result["edges"] = buffer_dict
            buffer_result["labels"] = buffer_list
            buffer_result["target"] = number_of_class
            result_list_of_dict.append(buffer_result)
        counter = 0
        for i in result_list_of_dict:
            out_name_str = out_names[counter] + ".json"
            self.file_out(i, out_name_str)
            counter += 1
        return ScResult.OK

    def file_out(self, input: dict, name: str):
        with open(name, 'w') as file:
            json.dump(input, file, indent=4)

    def agent(self, input: ScAddr):

        class_addr = input
        example_list = self.search_triple(class_addr)
        buffer_result = []
        for i in example_list:
            buffer_example_result = []
            buffer_example_result.append(i)
            buffer_example_result += self.search_triple(i)
            buffer_example_result += self.search_triple_with_norole_relation(i)
            buffer_example_result.append("__REVERSE")
            # buffer_example_result += self.search_triple_revers(i)
            buffer_example_result += self.search_triple_with_relation_reverse(i)
            print(buffer_example_result)
            for j in buffer_example_result:
                print(get_system_idtf(j))
            buffer_result.append(buffer_example_result)
        for i in buffer_result:
            for j in range(0, len(i) - 1):
                if type(i[j]) == type(class_addr):
                    if i[j] == class_addr:
                        i.pop(j)
        result = []
        for i in buffer_result:
            buffer_list = []
            for j in i:
                if type(j) == type(class_addr):
                    buffer_list.append(get_system_idtf(j))
                else:
                    buffer_list.append(j)
            result.append(buffer_list)
        return result
    def search_triple_with_norole_relation(self, input: ScAddr):
        result = []
        example_template = ScTemplate()
        example_template.triple_with_relation(input,
                                              sc_types.EDGE_D_COMMON_VAR,
                                              sc_types.NODE_VAR >> 'target',
                                              sc_types.EDGE_ACCESS_VAR_POS_PERM,
                                              sc_types.NODE_NOROLE)
        search_result = template_search(example_template)
        for i in search_result:
            result.append(i.get('target'))
        return result

    def search_triple_with_role_relation(self, input: ScAddr, relation: ScAddr):
        result = []
        example_template = ScTemplate()
        example_template.triple_with_relation(input,
                                              sc_types.EDGE_D_COMMON_VAR,
                                              sc_types.NODE_VAR >> 'target',
                                              sc_types.EDGE_ACCESS_VAR_POS_PERM,
                                              relation >> 'rrel')
        search_result = template_search(example_template)
        print(search_result)
        for i in search_result:
            result.append(int(
                get_system_idtf(i.get('rrel'))[5:]
            ))
            result.append(i.get('target'))
            print(get_system_idtf(i.get('target')))
        return result
    def search_triple_with_relation_reverse(self, input: ScAddr):
        result = []
        example_template = ScTemplate()
        example_template.triple_with_relation(sc_types.NODE_VAR >> 'target',
                                              sc_types.EDGE_D_COMMON_VAR,
                                              input,
                                              sc_types.EDGE_ACCESS_VAR_POS_PERM,
                                              sc_types.NODE_NOROLE)
        search_result = template_search(example_template)
        for i in search_result:
            result.append(i.get('target'))
        return result
    def search_triple(self, input: ScAddr):
        print(get_system_idtf(input))
        result = []
        example_template = ScTemplate()
        example_template.triple(input, sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.NODE_VAR >> 'target')
        search_result = template_search(example_template)
        for i in search_result:
            result.append(i.get('target'))
        return result
    # def search_triple_revers(self, input: ScAddr):
    #     result = []
    #     example_template = ScTemplate()
    #     example_template.triple(sc_types.NODE_VAR >> 'target', sc_types.EDGE_ACCESS_VAR_POS_PERM, input)
    #     search_result = template_search(example_template)
    #     print(len(search_result))
    #     for i in search_result:
    #         result.append(i.get('target'))
    #     return result
