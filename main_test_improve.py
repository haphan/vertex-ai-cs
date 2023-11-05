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
    context: str = ''
    source: str = ''

settings = Settings()


def test_load_questions(file: str, root_key = 'questions') -> List[str]:
    with open(file, 'r') as f:
        parsed_yaml = yaml.safe_load(f)
        return parsed_yaml[root_key] if parsed_yaml[root_key] else []
     
def test_runner(glob: str = './tests/*.yaml', root_key: str = 'questions') -> List[str]:
    for f in pathlib.Path('.').glob(glob):
        print(f)
        questions = test_load_questions(f)
        answers = run_questions(questions=questions)
        
        print([a.model_dump() for a in answers])

        
def run_questions(questions: List[str]) -> List[QuestionAnswerModel]:
    answers = []
    conversation = conversation_builder()

    for q in questions:
        print(f'>>>>>> Question: {q}')
        
        context, source, score = find_match(q)

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
                                    f"{q} \n"
                                    f"================\n"
                                    f"Trả lời:\n")
            response += f"\n\n\nNguồn: {source}"
        
        qa_model = QuestionAnswerModel(question=q, answer=response, source=source)
        answers.append(qa_model)       

    return answers


def save_conversation_to_file(file: str, answers: List[QuestionAnswerModel]):
    with open(file, 'w') as f:
        yaml.dump(answers, f)

def conversation_builder() -> ConversationChain:
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