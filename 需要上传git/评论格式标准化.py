import openai
import pandas as pd
import json
import time

openai.api_key = 'sk-Vn9HGTcg1wn1G2abvrCyYJQsvZnf2foaw1xjt5MHdhhptkRw'
openai.api_base = "https://api.chatanywhere.com.cn/v1"

# Read data from Excel file
def read_excel_data(file_path):
    df = pd.read_excel(file_path)
    return df['text'].tolist()

with open('./评论格式标准化.prompt', 'r', encoding='utf-8') as f:
    k = f.read()

# Make API call
def call_openai(prompt):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=3000,
        temperature=0.6,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].text

# Main function
file_path = '测试数据_1031.xlsx'  # Replace with your Excel file path
comments = read_excel_data(file_path)
responses = []
p = f"现在，请帮我分析以下评论内容，根据用户评论进行分析.：\n "
r = " "
for comment in comments:
    input_item = k + p + comment + r
    rsp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "一个很懂电商用户心理的AI"},
            {"role": "user", "content": input_item}
        ],
        max_tokens=600,
        temperature=0.6,
    )
    
    generated_response = rsp['choices'][0]['message']['content']
    print(generated_response)

    # Parsing the generated response
    lines = generated_response.strip().split('\n')
    
    # Extract headers (first line)
    header = [col.strip() for col in lines[0].strip('|').split('|')]

    # Map keywords in headers to specific columns
    header_mapping = {}
    for idx, col in enumerate(header):
        if '原评论' in col:
            header_mapping[idx] = '原评论'
        elif '评论' in col:
            header_mapping[idx] = '评论'
        # Add additional mappings here if needed
        else:
            header_mapping[idx] = col  # Use the original header name if no keyword match

    # Process the data rows
    for line in lines[2:]:  # Skip the header and separator lines
        row = [cell.strip() for cell in line.strip('|').split('|') if cell.strip()]

        # Adjust row length to match header length
        if len(row) < len(header):
            row.extend([''] * (len(header) - len(row)))
        elif len(row) > len(header):
            row = row[:len(header)]

        # Create a dictionary using the mapped headers
        response_dict = {header_mapping[i]: row[i] for i in range(len(header))}
        response_dict['评论'] = comment  # Add original comment to the response dictionary
        responses.append(response_dict)

# Save responses to a CSV file
response_df = pd.DataFrame(responses)
cols = ['评论'] + [col for col in response_df.columns if col != '评论']
response_df = response_df[cols]
response_df.to_csv('分析表格_4.csv', index=False, encoding='utf-8-sig')
