**直接在工作区打开就能用，完全不需要去改 Claude Code 的内部核心配置。**

Claude Code 本身就是一个具备自主运行终端命令、读取文件、编写和修改代码能力的命令行 Agent。你的这些 Python 脚本放在项目目录里，它就能通过内置能力调用它们。

具体的使用方式通常有以下两种：

**方式一：直接在对话中驱动脚本（最简单、最自然）**

不需要任何前置绑定，直接把它当成你终端里的“全自动程序员”：

1. 打开终端，进入你的建模代码目录，输入 `claude` 启动。
    
2. 确保你的工作区里有那些写好的脚本（如 `geometry_solver.py`、`strategy_planner.py`、`simulator_runner.py`）。
    
3. 直接用自然语言给它下指令：
    
    > “帮我运行 `python simulator_runner.py` 做一次模拟演练，然后读取输出的最新日志文件。根据日志里的平均清除耗时和遗漏干扰源，修改 `strategy_planner.py` 里的巡航路径生成算法，改完后再跑一次看看时间有没有缩短。”
    
4. **Claude Code 的内部行为**：
    
    - 它会调用内置的 `Bash` 工具自动执行 `python simulator_runner.py`。
        
    - 它会调用 `ReadFile` 工具自动解析生成的日志。
        
    - 它会调用 `Edit` 工具直接重写你的 `strategy_planner.py` 代码。
        

**方式二：通过 MCP 配置成严格的“自定义工具/Skill”（进阶）**

如果你希望把某些高频逻辑（比如“提取多边形直径”或“启动模拟器演练”）固定成 Claude Code 专属的原生指令，可以用 MCP（Model Context Protocol）接入：

1. **写一个极简的 MCP 包装**（用 `mcp` 库将你的 Python 函数暴露为服务）。
    
2. **在项目根目录创建或编辑配置文件**（`.claude.json` 或 Claude Code 的 MCP 配置文件）：
    
    JSON
    
    ```
    {
      "mcpServers": {
        "mcm_b_tools": {
          "command": "python",
          "args": ["path/to/my_mcp_server.py"]
        }
      }
    }
    ```
    
3. 这样一来，在 Claude Code 的工具箱里就会正式注册这些 Skill，它在规划时能更加稳定、结构化地按 Schema 传参调用。
    

**实战建议**

在数学建模竞赛这种争分夺秒的场景下，**优先采用方式一**：

- 只要保证脚本能用 `python script.py --args` 独立在终端跑通；
    
- 直接让 Claude Code 充当“主循环调度者”去反复执行、看结果、改代码，完全免去配置 MCP 的调试成本。