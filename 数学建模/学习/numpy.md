## 三、numpy 核心用法

### 3.1 numpy 是什么？

numpy 是 Python 的数值计算库，核心数据结构是 **ndarray**（多维数组）。

**类比**：numpy 数组就像"超级列表"，支持向量化运算，速度极快。

### 3.2 创建数组

```
import numpy as np

# 从列表创建
arr = np.array([1, 2, 3, 4, 5])

# 创建特殊数组
zeros = np.zeros(5)          # [0, 0, 0, 0, 0]
ones = np.ones(5)            # [1, 1, 1, 1, 1]
range_arr = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]

# 随机数组
random_arr = np.random.randn(100)  # 标准正态分布
```

### 3.3 数组运算

```
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# 向量化运算（不用循环！）
c = a + b          # [5, 7, 9]
d = a * b          # [4, 10, 18]
e = a ** 2         # [1, 4, 9]

# 标量运算
f = a * 10         # [10, 20, 30]
g = a + 5          # [6, 7, 8]
```

### 3.4 统计函数

```
arr = np.array([1, 2, 3, 4, 5])

print(arr.mean())     # 均值：3.0
print(arr.std())      # 标准差：1.414
print(arr.min())      # 最小值：1
print(arr.max())      # 最大值：5
print(arr.sum())      # 求和：15
print(arr.median())   # 中位数：3.0
```

### 3.5 条件筛选

```
arr = np.array([1, 2, 3, 4, 5])

# 布尔索引
mask = arr > 3        # [False, False, False, True, True]
result = arr[mask]    # [4, 5]

# 组合条件
result = arr[(arr > 2) & (arr < 5)]  # [3, 4]
```

### 3.6 与 pandas 的配合

```
# pandas 的列本质上是 numpy 数组
series = df['Y染色体浓度']
arr = series.values  # 转为 numpy 数组

# 用 numpy 计算
mean = np.mean(arr)
std = np.std(arr)

# 标准化
standardized = (arr - mean) / std
df['Y浓度_标准化'] = standardized
```