## 读取xlsx文件输出xlsx文件（暂时这样，有需要再改）
import pandas as pd
from datasketch import MinHash, MinHashLSH
from tqdm import tqdm

# 读取Excel文件
file_path = 'merged_output_1025.xlsx'
df = pd.read_excel(file_path)

# 过滤评论长度大于15，并去重，同时删除包含特定文本的项
# 删除含特定字段评论这部分是特别针对拼多多评论数据的（因为其中这些项会混淆结果，增加难度和运行时间）
df = df[df['评论'].str.len() > 15]
df = df[~df['评论'].str.contains('该用户觉得商品很好')]
df = df[~df['评论'].str.contains('该用户未填写评论')]
df = df[~df['评论'].str.contains('该用户未填写文字评论')]
df = df[~df['评论'].str.contains('该用户觉得商品较好')]
df = df['评论'].drop_duplicates().reset_index(drop=True).reset_index()

# 添加序号列
df['序号'] = df.index
# 确保“序号”和“评论”列存在
if '序号' not in df.columns or '评论' not in df.columns:
    raise ValueError("Excel文件中没有找到‘序号’或‘评论’列")

# 使用 MinHash 和 LSH 进行近似匹配
## 注意！！！需要修改的参数在这里，目前测试出来对于 评论 精筛用0.8，粗筛用0.65； 对于 微博数据 精筛用0.9，粗筛用0.8-0.85
lsh = MinHashLSH(threshold=0.65, num_perm=128)

# 将评论转换为 MinHash
minhashes = []
for comment in tqdm(df['评论'], desc='计算MinHash'):
    m = MinHash()
    for word in comment.split():
        m.update(word.encode('utf8'))
    minhashes.append(m)

# 将 MinHash 添加到 LSH
for i, minhash in enumerate(tqdm(minhashes, desc='插入LSH')):
    lsh.insert(i, minhash)

# 查找匹配的评论
matched_comments_list = []
for i, minhash in enumerate(tqdm(minhashes, desc='查询匹配')):
    result = lsh.query(minhash)
    for j in result:
        if i < j: 
            matched_comments_list.append({
                '评论编号1': df.iloc[i]['序号'],
                '评论编号2': df.iloc[j]['序号'],
                '评论内容1': df.iloc[i]['评论'],
                '评论内容2': df.iloc[j]['评论']
            })
    if i % 100 == 0:
        print(f"已完成 {i} 条评论的匹配")

# 将列表转换为 DataFrame
matched_comments = pd.DataFrame(matched_comments_list)

# 如果没有匹配的评论对，则不保存文件
if not matched_comments.empty:
    output_file_path = 'matched_comments_1028_零点65.xlsx'
    matched_comments.to_excel(output_file_path, index=False)
    print(f"匹配分数大于90的评论对已保存到 '{output_file_path}'")
else:
    print("没有找到匹配分数大于90的评论对。")