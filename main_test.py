import pathlib
import yaml
from pydantic import BaseModel
from settings import Settings
from typing import List, Optional

from utils import *
from langchain.chat_models import ChatVertexAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)

class QuestionAnswerModel(BaseModel):
    question: str
    answer: str
    source: str = ''
    refined_query: str = ''

settings = Settings()

def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)
yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

def test_load_questions(file: str, root_key = 'questions') -> List[str]:
    with open(file, 'r') as f:
        parsed_yaml = yaml.safe_load(f)
        return parsed_yaml[root_key] if parsed_yaml[root_key] else []
     
def test_runner(glob: str = './tests/*.yaml', root_key: str = 'questions', save_test_outout = True) -> List[str]:
    for f in pathlib.Path('.').glob(glob):
        print(f)
        questions = test_load_questions(f)
        answers = run_questions(questions=questions)
        
        if save_test_outout:
            test_file_path = (pathlib.Path(f)).name
            test_out_file_path = pathlib.Path(f'./tests_output/{test_file_path}')
            test_out_file_path.parent.mkdir(exist_ok=True, parents=True)

            save_conversation_to_file(file=str(test_out_file_path.absolute()), answers=[a.model_dump() for a in answers])

        
def run_questions(questions: List[str]) -> List[QuestionAnswerModel]:
    answers = []
    buff_memory=ConversationBufferWindowMemory(k=3,return_messages=True)
    conversation = conversation_builder(buff_memory=buff_memory)

    for q in questions:
        print(f'>>>>>> Question: {q}')
        print(f'>>>>> History: {buff_memory.buffer_as_str}')
        refined_query = query_refiner(buff_memory.buffer_as_str, q)

        context, source, score = find_match(refined_query)

        if score < settings.trust_score_min:
            response = settings.prompt_template.default_no_answer
        else:    
            response = conversation.predict(
                                input=f""
                                    f"Ngữ cảnh:\n"
                                    f"================\n"
                                    f"{context}\n"
                                    f"================\n"
                                    f"Câu hỏi:\n"
                                    f"================\n"
                                    f"{refined_query} \n"
                                    f"================\n"
                                    f"Trả lời:\n")
            buff_memory.save_context({'input': q}, {'output': response})
            buff_memory.load_memory_variables({})
        
        qa_model = QuestionAnswerModel(question=q, answer=response, source=source, refined_query=refined_query)
        answers.append(qa_model)       

    return answers


def save_conversation_to_file(file: str, answers: List):
    with open(file, 'w') as f:
        print(yaml.dump(answers, f, allow_unicode=True))



def conversation_builder(buff_memory) -> ConversationChain:
    llm = ChatVertexAI(model_name=settings.llm_model_chat, 
                max_output_tokens=settings.llm_max_output_tokens, 
                temperature=settings.llm_temperature, 
                top_p=settings.llm_top_p,
                top_k=settings.llm_top_k
            )
    buff_memory = ConversationBufferWindowMemory(k=3,return_messages=True)

    system_msg_template = SystemMessagePromptTemplate.from_template(template=settings.prompt_template.system)
    human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")
    prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])
    conversation = ConversationChain(memory=buff_memory, prompt=prompt_template, llm=llm, verbose=True)

    return conversation


def main():
    test_runner()

if __name__ == "__main__":
    main()