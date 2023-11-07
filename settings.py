from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class PromptTemplateModel(BaseModel):
    system: str ="""
Tôi là Linh, nhân viên chăm sóc khách hàng.
Tôi chỉ trả lời những câu hỏi có liên quan đến ngữ cảnh hiện tại.
Nếu câu hỏi không liên quan, tôi sẽ yêu cầu khách hàng đặt lại câu hỏi rõ hơn.
Tôi không cung cấp đường dẫn đến trang web.
Câu trả lời của tôi phải luôn ngắn gọn, không quá 200 chữ.
Tôi luôn lịch sự, kết thúc câu trả lời bằng lời cảm ơn.
Tôi gọi khách hàng bằng "anh/chị".
Tôi sử dụng emoji trong tất cả các câu trả lời.
"""
    default_no_answer: str = 'Dạ, em chưa có thông tin về câu hỏi này.'
    
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    llm_model_embedding: str = 'textembedding-gecko-multilingual@latest'
    llm_model_chat: str = 'chat-bison'
    llm_max_output_tokens: int = 1024
    llm_temperature:float = 0.01
    llm_top_p: float = 0.95 
    llm_top_k: int = 40

    trust_score_min: float = 0.75

    pinecone_api_key: str
    pinecone_env: str
    pinecone_idx: str

    streamlit_page_title: str = 'OnPoint Customer Service'
    streamlit_header: str = 'OnPoint Customer Service 🦸 🦸‍♀️'
    streamlit_welcome_msg: str = 'Em là Linh - nhân viên hỗ trợ cho OnPoint. Em có thể giúp gì cho anh/chị?'
    
    prompt_template: PromptTemplateModel = PromptTemplateModel()


