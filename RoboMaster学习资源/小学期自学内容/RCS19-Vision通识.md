在此之前需要大家开动脑筋学习一下科学上网。可以私信问各个学长。
# 1. Git 通用

Linux 可以暂时不做实践要求，但是要求对以下命令起码要有印象，git 要求大家都要掌握。
Vscode/Visual Studio 对电控，视觉有更高要求，但是通识标准是一样的。
需要掌握： 会使用 Linux 基本命令：cd、ls、mkdir、cp、rm、grep 
会使用 Git 基本命令：clone、pull、status、diff 
会用 VSCode 打开工程、搜索文件、查看函数定义 会看终端报错，能描述自己遇到了什么问题。

## 1.1 需要掌握的 Linux 基础

### 必须会的命令

```
pwd              # 查看当前所在目录
ls               # 查看当前目录下有什么
ls -la           # 查看隐藏文件和详细信息
cd <目录名>       # 进入某个目录
cd ..            # 回到上一级目录
mkdir <目录名>    # 创建文件夹
touch <文件名>    # 创建空文件
cp 源文件 目标位置 # 复制文件
cp -r 源目录 目标位置 # 复制文件夹
mv 源文件 目标位置 # 移动或重命名
rm <文件名>       # 删除文件
rm -r <目录名>    # 删除文件夹
cat <文件名>      # 查看文件内容
less <文件名>     # 分页查看文件
grep "关键词" 文件名 # 在文件中搜索关键词
find . -name "*.cpp" # 在当前目录下查找 cpp 文件
```

### 需要理解的概念

```
当前目录：你现在所在的位置
上一级目录：..
根目录：~
绝对路径：从 / 开始的完整路径
相对路径：从当前目录出发的路径
隐藏文件：以 . 开头的文件，例如 .git
```

### 安全提醒

不要乱用：

```
sudo rm -rf /
rm -rf *
```

除非你想让你的 Linux 爆炸。

---

## 1.2 需要掌握的 Git 基础

### 必须会的命令

```
git clone <仓库链接>     # 下载仓库
git status              # 查看当前修改状态
git diff                # 查看自己改了什么
git pull                # 拉取远端最新代码
git add <文件名>         # 把修改加入暂存区
git commit -m "说明"    # 提交一次修改
git log --oneline       # 查看提交记录
git branch              # 查看当前分支
git checkout <分支名>    # 切换分支
```
可以想想假设你有一个新项目（视觉，电控代码，硬件原理图或机械图），想要推送到远端仓库，需要怎么做。
```
# 在当前项目文件夹下
git add .
git commit -m "initial commit"
git push origin main
```
### 暂时不要求掌握，但需要听说过

```
# 这些很难的，暂时不会可以。
git merge
git rebase
git stash
git reset
git cherry-pick
```

---

## 1.3 VS Code 基本使用

需要会：

- 用 VS Code 打开整个工程文件夹
- 用搜索功能查找关键词
- 用 Ctrl + 鼠标左键跳转函数定义
- 用 Ctrl + Shift + F 全局搜索
- 看左侧文件树
- 看终端输出
- 能复制完整报错信息

推荐安装插件：

```
Python
C/C++
CMake Tools
Python
ROS2
GitLens
```

---

## 1.4 推荐资料

### 参考资料
这边的参考资料大而全，不一定适合所有人，所以
1. Linux 命令行入门  
    Ubuntu 官方教程：  
    [https://ubuntu.com/tutorials/command-line-for-beginners](https://ubuntu.com/tutorials/command-line-for-beginners)

建议只看这些内容：

```
Opening a terminal
Creating folders and files
Moving and manipulating files
Hidden files
```

2. Git 交互式练习  这个类似于游戏
    [https://learngitbranching.js.org/?locale=zh_CN](https://learngitbranching.js.org/?locale=zh_CN)

建议完成：

```
主要关卡：前 4 个基础关卡
重点理解：commit、branch、checkout、merge
```

3. Git 官方中文书  
    [https://git-scm.com/book/zh/v2](https://git-scm.com/book/zh/v2)

建议只看：

```
1.1 关于版本控制
1.5 安装 Git
1.6 初次运行 Git 前的配置
2.1 获取 Git 仓库
2.2 记录每次更新到仓库
2.3 查看提交历史
2.5 远程仓库的使用
```

4. VS Code 代码导航  
    [https://code.visualstudio.com/docs/editing/editingevolved](https://code.visualstudio.com/docs/editing/editingevolved)

重点看：

```
Go to Definition
Peek Definition
Find All References
Symbol Search
```

### 视频推荐方式

视频不用追求完整课程，这里简单推荐一些视频。


[Linux 基础命令 入门](https://www.bilibili.com/video/BV1cq421w72c/?spm_id_from=333.337.search-card.all.click&vd_source=2812f2dba8b6d88393ee140cbf8b848e)

https://www.bilibili.com/video/BV1Uv4y127tU/?spm_id_from=333.337.search-card.all.click

[Git 入门]https://www.bilibili.com/video/BV1Hkr7YYEh8/?spm_id_from=333.337.search-card.all.click&vd_source=2812f2dba8b6d88393ee140cbf8b848e

https://www.bilibili.com/video/BV1FE411P7B3/?spm_id_from=333.337.search-card.all.click&vd_source=2812f2dba8b6d88393ee140cbf8b848e


VS Code 很多，这里不做推荐
```

## 1.5 自学时建议完成的小任务

### 任务 1：熟悉目录操作

假设 Linux 上创建一个练习目录：

```
mkdir rm_vision_practice
cd rm_vision_practice
mkdir src include config
touch README.md
ls -la
```

然后尝试：

```
cp README.md README_copy.md
mv README_copy.md note.md
rm note.md
```

要求：能说清楚每条命令做了什么。这一个任务可以不做实操要求。

---


### 任务 2：clone 一个你喜欢的项目并查看状态

```
git clone <训练仓库链接>
cd <仓库目录>
git status
git log --oneline
```

然后随便改一个 README 文件，再执行：

```
git status
git diff
```

要求：能看懂 Git 提示“哪些文件被修改了”。

---

### 任务 3：写一次规范提问

遇到报错时，不要只发一句“跑不了”。按照下面格式提问：

```
我想做什么：
我执行了什么命令：
完整报错信息：
我已经尝试了什么：
我猜可能是什么原因：
```

示例：

```
我想做什么：clone 仓库并编译。
我执行了什么命令：colcon build --symlink-install
完整报错信息：找不到 xxx.hpp
我猜可能是什么原因：可能依赖没有安装，或者 include 路径不对。
```

---

## 1.6 本部分验收要求

完成本部分后，应该能做到：

```
1. 能打开终端并进入指定目录
2. 能创建、复制、删除、查找文件
3. 能 clone 一个 Git 仓库
4. 能用 git status 和 git diff 查看自己改了什么
5. 能用 VS Code 打开工程并搜索函数
6. 能复制完整报错，并用规范格式提问
```

最低考核方式：

```
1. 了解以上基础命令并给出解释
2. clone 一个仓库
3. 修改 README
4. 用 git status 和 git diff 展示修改
5. 用 VS Code 搜索一个函数或关键词
6. 按规范格式描述一次假想报错
```

本部分不要求掌握复杂 Git 分支管理，也不要求会 Linux 系统管理。先做到能进入工程现场，不迷路，不乱删文件，能说清问题即可。

# 2. C++ 最小基础

本部分目标不是让大家精通 C++，也不是准备课内考试。  
目标只有一个：能看懂项目里的 C++ 代码，知道函数、类、消息结构、配置参数大概是怎么流动的。
建议方式：边看资料边写小 demo，不要只看视频，不要硬背语法细节。

---

## 2.1 需要掌握到什么程度

两周内只要求达到“能读代码”的程度，不要求掌握模板元编程、复杂继承、设计模式、STL 全家桶。

需要掌握：

```text
1. 能看懂一个函数的输入和输出
2. 能看懂 if / for / while 的控制逻辑
3. 能看懂 struct / class 里有哪些成员变量和成员函数
4. 能看懂 std::vector、std::string 的常见用法
5. 能大概理解引用 & 和指针 *
6. 能知道 .hpp 和 .cpp 的关系
7. 能知道 namespace 是为了避免名字冲突
8. 能看懂 include 是在引入头文件
9. 能看懂代码里对象之间如何传数据
```

不要求掌握：

```text
1. 模板高级用法
2. 多重继承
3. 运算符重载
4. 手写智能指针
5. C++ 内存模型
6. 复杂并发编程
7. C++20 / C++23 新特性
```

---

## 2.2 必须掌握的 C++ 基础

### 1. 函数 function

需要知道：

```cpp
int add(int a, int b)
{
    return a + b;
}
```

重点理解：

```text
int：返回值类型
add：函数名
int a, int b：输入参数
return：返回结果
```

---

### 2. if / for / while

需要能看懂条件判断和循环。

```cpp
if (target_valid) {
    fire = true;
} else {
    fire = false;
}
```

```cpp
for (const auto& armor : armors) {
    // 遍历所有检测到的装甲板
}
```
---

### 3. struct

`struct` 可以理解为“把一组相关数据打包”。

```cpp
struct ArmorObservation {
    int id;
    double x;
    double y;
    double z;
};
```

---

### 4. class

`class` 可以理解为“数据 + 操作这些数据的函数”。

```cpp
class Tracker {
public:
    void update(double x, double y);
    bool is_tracking() const;

private:
    double last_x;
    double last_y;
};
```

---

### 5. std::vector

`std::vector` 可以理解为“长度可以变化的数组”。

```cpp
std::vector<int> nums;
nums.push_back(1);
nums.push_back(2);
```

遍历 vector：

```cpp
for (const auto& x : nums) {
    std::cout << x << std::endl;
}
```

---

### 6. std::string

`std::string` 是字符串。
```cpp
std::string name = "autoaim";
```

---

### 7. 引用 &

引用可以先粗略理解成“给变量起了一个别名”。

```cpp
void update(int& x)
{
    x = x + 1;
}
```

调用后，原来的 x 会被改变。

常见写法：

```cpp
void process(const std::vector<int>& data)
```

这里的意思是：

```text
const：函数里不修改 data
&：不复制一整份 vector，提高效率
const T& 常用于只读传参
T& 常用于函数内部会修改外部变量
```

---

### 8. 指针 *

指针可以先粗略理解成“保存某个对象地址的变量”。

```cpp
int a = 10;
int* p = &a;
```

在现代 C++ 项目里，更常见到的是智能指针：

```cpp
std::shared_ptr<Tracker> tracker;
```

可以先理解为：

```text
shared_ptr：多个地方共享使用同一个对象
unique_ptr：这个对象只归一个地方管理
```

不要求一开始完全理解内存管理，先能看懂代码里这个对象是被指针管理的即可。

---

### 9. .hpp 和 .cpp

一般可以这样理解：

```text
.hpp：声明这个模块有什么
.cpp：实现这个模块具体怎么做
```

例如：

```text
tracker.hpp：声明 Tracker 类有哪些函数
tracker.cpp：实现 Tracker 的 update / reset 等函数
```

读代码时建议顺序：

```text
先看 .hpp，知道这个类对外提供什么能力
再看 .cpp，知道每个函数具体怎么实现
```

---

### 10. namespace

`namespace` 用来避免名字冲突。

```cpp
namespace rm_autoaim {
    class Tracker {};
}
```

调用时可能写成：

```cpp
rm_autoaim::Tracker tracker;
```

namespace 是代码所在的命名空间
:: 表示从某个命名空间或类里面取东西

---

## 2.3 推荐资料

### 参考资料

1. LearnCpp  
    [https://www.learncpp.com/](https://www.learncpp.com/)
    

建议只看这些内容：

```text
Chapter 0：Introduction / Getting Started
Chapter 1：C++ Basics
Chapter 2：Functions and Files
Chapter 3：Debugging C++ Programs
Chapter 5：Introduction to std::string
Chapter 8：If statements / switch / control flow
```

不需要完整刷完，先挑和项目有关的内容看。

---

2. cppreference
    

[https://en.cppreference.com/](https://en.cppreference.com/)

这是 C++ 标准库查询网站，不适合从头学习，但适合查用法。

建议查：

```text
std::vector
std::string
std::shared_ptr
std::unique_ptr
```

看不懂没关系，能知道这是查标准库用法的网站即可。

---

3. Microsoft C++ 文档
    

[https://learn.microsoft.com/en-us/cpp/cpp/?view=msvc-170](https://learn.microsoft.com/en-us/cpp/cpp/?view=msvc-170)

适合查：

```text
class
pointer
reference
namespace
function
```

---

### 视频推荐关键词

B 站搜索：

```text
[现代C++基础比较深 建议只看到04 或找对应需要的章节](https://www.bilibili.com/video/BV1pT4m1S7d8/?spm_id_from=333.337.search-card.all.click&vd_source=2812f2dba8b6d88393ee140cbf8b848e)

https://www.bilibili.com/video/BV1Fz421q7oh/?spm_id_from=333.337.search-card.all.click
```
或菜鸟教程搜cpp（当初我入门用的这个）。

---

## 2.4 建议完成的小任务

### 任务 1：写一个最简单的目标选择函数
这里以装甲板为例，可以自己挑选别的例子。

```cpp
#include <iostream>
#include <vector>
#include <string>

struct Armor {
    int id;
    std::string color;
    double distance;
};

Armor select_nearest_blue(const std::vector<Armor>& armors)
{
    Armor best{-1, "none", 9999.0};

    for (const auto& armor : armors) {
        if (armor.color == "blue" && armor.distance < best.distance) {
            best = armor;
        }
    }

    return best;
}

int main()
{
    std::vector<Armor> armors = {
        {1, "blue", 3.2},
        {2, "blue", 5.1},
        {3, "red", 2.7}
    };

    Armor target = select_nearest_blue(armors);

    std::cout << "selected target id = " << target.id << std::endl;

    return 0;
}
```

要求：能解释这个函数如何选择目标。

---

## 2.5 看项目代码时的建议

读 C++ 项目不要从第一行读到最后一行。建议按下面顺序：

```text
1. 先找 main / node / launch 启动入口
2. 再看 callback 函数
3. 再看 callback 里面调用了哪些模块
4. 最后再深入具体算法函数
```

遇到看不懂的代码，先问这三个问题：

```text
1. 这个变量是什么类型？
2. 这个函数输入是什么，输出是什么？
3. 这段代码是在改变状态，还是在计算结果？
```

不要一上来纠结每个语法细节。

---

## 2.6 本部分验收要求

完成本部分后，应该能做到：

```text
1. 能写一个简单 C++ 程序并运行
2. 能看懂函数输入和输出
3. 能看懂 struct / class 的基本结构
4. 能用 vector 保存多个目标
5. 能解释 .hpp 和 .cpp 的关系
6. 能读懂一段简单的自瞄数据处理代码
```

考核方式：

```text
1. 写一个 Armor struct
2. 解释 const std::vector<Armor>& armors 是什么意思
3. 解释 .hpp 和 .cpp 分别放什么
```

本部分不考复杂 C++ 语法。能读懂、能改小代码、能把问题讲清楚，就是合格。
