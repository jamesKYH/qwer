import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

# 데이터프레임을 캐싱하는 함수
@st.cache_data
def load_data():
    return pd.read_excel('/Users/james_kyh/Downloads/AdidasSalesdata.xlsx')

# 캐싱된 데이터프레임을 불러옴
df = load_data()

# GPT에게 우리가 다루는 데이터프레임이 어떤 구조인지 알려주는 함수 작성
# 아래 컬럼 기준으로 코드를 작성해줄 것 요청
def table_definition_prompt(df):
    prompt = '''Given the following pandas dataframe definition,
            write queries based on the request
            \n### pandas dataframe, with its properties:
            
            #
            # df의 컬럼명({})
            #
            
            '''.format(",".join(str(x) for x in df.columns))
    
    return prompt

nlp_text = st.text_input('질문을 입력하세요: ')
accept = st.button('요청')

if accept:
    full_prompt = str(table_definition_prompt(df)) + str(nlp_text)


    # API 호출
    #  R T F C 프레임워크
    #  Role : AI가 수행할 역할을 명확히 정의
    #  Task : 수행할 구체적인 작업 기술
    #  Format : 결과물의 형식과 길이를 지정 
    #  Constraints : 준수해야할 규칙과 제한을 명시
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that generates Pandas boolean indexing code based on the given df definition\
            and a natural language request. The answer should start with df and contains only code by one line, not any explanation or ``` for copy."},
            {"role": "user", "content": f"A query to answer: {full_prompt}"}
        ],
        max_tokens=200, # 비용 발생하므로 시도하며 적당한 값 찾아간다. 200이면 최대 200단어까지 생성. 
                        # 영어는 한 단어가 1토큰, 한글은 한 글자가 1토큰 정도
        temperature=1.0, # 창의성 발휘 여부. 0~2 사이. 0에 가까우면 strict하게, 2에 가까우면 자유롭게(창의성 필요)
        stop=None # 특정 문자열이 들어오면 멈춘다든지. None이면 없음. .이면 문장이 끝나면 멈춘다든지
        )


    answer = response.choices[0].message.content

    st.code(full_prompt)

    st.code(answer)

    # eval 함수를 사용하여 문자열로 된  ' '를 벗겨내고 코드 자체로 실행
    st.write(eval(answer))
    