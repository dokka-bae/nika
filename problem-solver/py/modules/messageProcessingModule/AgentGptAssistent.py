from sc_client.models import ScAddr
from sc_kpm import ScResult
import sc_kpm
import g4f
from sc_client.models import *
from sc_client.constants import sc_types
from sc_client.client import *
from typing import List, Union
import logging
import sc_client
from sc_kpm import ScAgentClassic
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class AgentGptAssistent(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__('action_solve_message_request')
        self.logger.info("Created AgentGptAssistent")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.action_node = action_element
        self.__create_struct_node()
        self.logger.info("AgentGptAssistent started")
        result = self.__run(action_element)
        self.logger.info("AgentGptAssistent finished")
        return result

    def __create_struct_node(self):
        construction = ScConstruction()
        construction.create_node(sc_types.NODE_CONST_NOROLE) # creating nrel_answer node
        nrel_answer_node = sc_client.client.create_elements(construction)[0]

        construction = ScConstruction()
        construction.create_node(sc_types.NODE_CONST_STRUCT) # creating struct node
        self.struct_node = sc_client.client.create_elements(construction)[0]

        construction = ScConstruction()
        construction.create_edge(sc_types.EDGE_D_COMMON_CONST,self.action_node,self.struct_node) # create edge bt act&struct
        edge_common_d = sc_client.client.create_elements(construction)[0]

        construction = ScConstruction()
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,nrel_answer_node,edge_common_d) # connect nrel_answer&edge
        sc_client.client.create_elements(construction)

    def __get_model(self) -> str:
        template = ScTemplate()
        template.triple_with_relation(
            self._struct_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes["nrel_using_model"],
        )
        model_node = template_search(template)
        template = ScTemplate()
        template.triple_with_relation(
            model_node[0][2],
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.LINK_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR_NOROLE,
        )
        link_node = template_search(template)
        model = sc_kpm.utils.get_link_content_data(link_node[0][2])
        return model

    def __get_message(self) -> str:
        template = ScTemplate()
        template.triple_with_relation(
            self._struct_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes["nrel_message"],
        )
        message_node = template_search(template)
        template = ScTemplate()
        template.triple_with_relation(
            message_node[0][2],
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.LINK_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR_NOROLE,
        )
        link_node = template_search(template)
        message = sc_kpm.utils.get_link_content_data(link_node[0][2])
        return message

    def __get_params(self) -> str:
        request_message = self.__get_message()
        model = self.__get_model()
        return request_message, model

    def __run(self,action_node: ScAddr) -> None:
        template = ScTemplate()
        template.triple(
            action_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR_STRUCT,
        )
        self._struct_node = template_search(template)[0][2]
        message, model = self.__get_params()
        response = g4f.ChatCompletion.create(
            model, messages=[{"role": "user", "content": message}], stream=True
        )
        self._answer = []
        for message in response:
            self._answer.append(message)
        print("".join(self._answer))

        

        construction = ScConstruction()
        construction.create_link(sc_types.LINK_CONST, content = ScLinkContent("".join(self._answer), ScLinkContentType.STRING)) # main tuple node
        link_node = sc_client.client.create_elements(construction)[0]

        construction = ScConstruction()
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,self.struct_node,link_node)
        sc_client.client.create_elements(construction)[0]


        return ScResult.OK


def main():
    url = "ws://localhost:8090/ws_json"
    connect(url)
    AgentGptAssistent()


if __name__ == "__main__":
    main()
