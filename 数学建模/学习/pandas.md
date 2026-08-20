## 二、pandas 核心用法

### 2.1 pandas 是什么？

pandas 是 Python 的数据处理库，核心数据结构是 **DataFrame**（数据框）。

**类比**：DataFrame 就像一个"超级 Excel 表格"，但可以用代码操作。

### 2.2 读取数据

```
import pandas as pd

# 读取 Excel
df = pd.read_excel('附件.xlsx', sheet_name='男胎检测数据')

# 读取 CSV
df = pd.read_csv('男胎_全部数据.csv')

# 查看基本信息
print(df.shape)        # (行数, 列数)
print(df.head())       # 前5行
print(df.columns)      # 列名
print(df.dtypes)       # 每列的数据类型
```

### 2.3 选择数据

```
# 选择单列（返回 Series）
age = df['年龄']

# 选择多列（返回 DataFrame）
subset = df[['年龄', '身高', '体重']]

# 按条件筛选行
high_bmi = df[df['孕妇BMI'] > 35]

# 按位置选择（第0行，第2列）
value = df.iloc[0, 2]

# 按标签选择（第0行，'年龄'列）
value = df.loc[0, '年龄']
```

### 2.4 添加/修改列

```
# 添加新列
df['孕周_数值'] = df['检测孕周'].apply(parse_week)

# 修改现有列
df['胎儿是否健康'] = (df['胎儿是否健康'] == '是').astype(int)

# 删除列
df = df.drop(columns=['不需要的列'])
```

### 2.5 分组聚合

```
# 按孕妇代码分组，计算每组的平均值
avg = df.groupby('孕妇代码')['Y染色体浓度'].mean()

# 多列聚合
stats = df.groupby('孕妇代码').agg({
    'Y染色体浓度': 'mean',
    '孕妇BMI': 'first',
    '检测序号': 'count'
})

# 添加检测序号（组内累计计数）
df['检测序号'] = df.groupby('孕妇代码').cumcount() + 1
```

### 2.6 处理缺失值

```
# 查看缺失值
missing = df.isnull().sum()

# 填充缺失值
df['列名'] = df['列名'].fillna(0)           # 用0填充
df['列名'] = df['列名'].fillna(method='ffill')  # 用前一个值填充
df['列名'] = df['列名'].combine_first(other)    # 用另一列填充

# 删除缺失值
df_clean = df.dropna()                      # 删除任何有缺失的行
df_clean = df.dropna(subset=['BMI'])        # 只检查BMI列
```

### 2.7 数据转换

```
# apply：对每个元素应用函数
df['孕周_数值'] = df['检测孕周'].apply(parse_week)

# map：用字典映射
health_map = {'是': 1, '否': 0}
df['健康_数值'] = df['胎儿是否健康'].map(health_map)

# astype：类型转换
df['怀孕次数'] = df['怀孕次数'].astype(float)

# 字符串操作
df['孕周'].str.upper()      # 转大写
df['孕周'].str.contains('w')  # 包含某字符
```



## 五、常用操作速查表

|操作|pandas 代码|说明|
|---|---|---|
|读取 Excel|`pd.read_excel('file.xlsx')`|读取 Excel 文件|
|读取 CSV|`pd.read_csv('file.csv')`|读取 CSV 文件|
|查看前5行|`df.head()`|查看数据|
|查看形状|`df.shape`|(行数, 列数)|
|查看列名|`df.columns`|所有列名|
|查看类型|`df.dtypes`|每列的数据类型|
|选择列|`df['列名']`|选择单列|
|筛选行|`df[df['列'] > 值]`|条件筛选|
|添加列|`df['新列'] = ...`|添加新列|
|删除列|`df.drop(columns=['列'])`|删除列|
|分组|`df.groupby('列')`|按列分组|
|聚合|`.agg({'列': 'mean'})`|聚合计算|
|缺失值|`df.isnull().sum()`|统计缺失|
|填充缺失|`df.fillna(值)`|填充缺失值|
|应用函数|`df['列'].apply(func)`|对每行应用函数|
|类型转换|`df['列'].astype(int)`|转换数据类型|
|保存 CSV|`df.to_csv('file.csv')`|保存为 CSV|
|保存 Excel|`df.to_excel('file.xlsx')`|保存为 Excel|