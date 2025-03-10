# **1、MoFA开发框架**  
## **1.1  **框架核心手册**  

### **1.1.1 设计理念**

MoFA是一个以组合的方式构建AI智能体的软件框架。使用MoFA，AI智能体可以通过模版方式构建，堆叠的方式组合，形成更强大的超级智能体（Super Agent)。

MoFA 独特的设计类理念是：

- **平凡人做非凡事**：AI 不该是精英和巨头的专属领地。MoFA 让每个人都能驾驭和发展 AI，把不可能变成可能，让平凡人也能创造非凡。
- **Composition AI**：受 Unix 哲学启发，MoFA 以“组合”作为核心原则。你可以像搭积木一样，构建智能体、连接智能体、集成工具，让 AI 变得简单、灵活、强大。
- **Everything Agent**：与绝大多数软件不同，在 MoFA 的世界里，智能体（Agent）就是 AI 时代的应用（Application）。不仅是大语言模型，它可以是代码、脚本、API，甚至是 MoFA 本身。MoFA 不是一个框架，而是一个 Agent 生态。
- **Data Flow**：大多数智能体框架依赖复杂的工作流（WorkFlow），而 MoFA 选择更直观、更强大的数据流（Data Flow）。这种方式让智能体能自由组合、拆解和重用，

### **1.1.2 技术架构图**

<img src="./images/image-20250310010710778.png" alt="image-20250310010710778" style="zoom:67%;" />

# 2. **快速上手指南**

## **2.1 开发环境准备**

### 2.1.1 Python 环境
```bash
# 安装 UV 包管理器 加快mofa安装
pip install uv
```

**注意**: 
-  如果你的环境是conda的话,由于dora可能在不同系统中对多python环境支持可能存在问题，您需要在默认的base环境安装mofa
- 要求python环境 >= 3.10 

### 2.1.2 Rust 环境
```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Dora 运行时
cargo install dora-cli

# 验证安装
rustc --version
cargo --version
dora --version
```

## 2.2 安装 MoFa

### 2.2.1 Git Clone 方式
```bash
# 克隆仓库
git clone https://github.com/moxin-org/mofa.git
cd mofa/python

# 安装依赖
uv pip install -e .
pip install -e . 
```

### 2.2.2 Docker 方式
```bash
# 进入docker目录
cd /mofa/python/docker
# 构建镜像
docker build -t mofa -f Dockerfile_x86 .

# 运行容器
docker run -it --rm mofa

# 在容器内验证安装
mofa --help 
```

## **2.3 运行第一个Hello World**


### 2.3.1 启动数据流
```bash
cd  /project/mofa/python/examples/hello_world

# 启动 Dora 服务
dora up

# 构建并运行数据流
dora build hello_world_dataflow.yml
dora start hello_world_dataflow.yml
```

### 2.3.2 测试交互
```bash
# 在另一个终端运行输入节点
terminal-input

# 输入测试数据
> hello
# 预期输出: hello
```

### 2.3.3 **运行效果**

```
root@root hello_world % terminal-input                                           
 Send You Task :  你好
-------------hello_world_result---------------    
你好 
---------------------------------------  
 Send You Task :  你是谁   
-------------hello_world_result---------------    
你是谁    
---------------------------------------
```

## **2.4 开发第一个应用**

5分钟创建问答机器人  基于pymofa

# **3. 高级开发手册**

## 3.1 **构建自定义 Agent**

 基于pymofa, 如何开发我们agent-hub的代码

rss
网页爬虫

---
### **二、案例体系设计**
#### 1. **基础教学案例库**
- 案例1：arxiv_research
- 案例2：deep-inquire
- 案例3：deepseek_serper

将这些代码迁移到mofa-search

#### 2. **黑客松专题案例**
- 案例4：MoFA Planning
- 案例5：MoFA Tool Use

mofa-search里面

---
### **三、黑客松专项支持**
#### 1. **赛前训练营**
- 直播课程：
  - 框架核心API详解
  - 往届优秀项目代码拆解

---
### **四、生态建设配套**
- 社区支持：
-