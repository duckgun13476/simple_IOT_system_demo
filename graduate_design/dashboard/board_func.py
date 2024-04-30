website_prompt = """
**作者的话：**
欢迎来到我的云端仪表检测面板示例网站。本站点提供了一套用于实时监控和管理仪表数据的功能，目前已实现的功能包括：

1. **仪表日志图表**：查看仪表数据的历史记录和趋势，支持多种图表展示。
2. **数据读取**：实时从仪表中读取数据，确保您能够即时获取最新信息。
3. **状态检测**：监测仪表的当前状态，包括但不限于开/关状态、性能指标等。
4. **数据库存储**：所有仪表数据都会被安全地存储在云端数据库中，便于历史数据的查询和分析。
5. **仪表状态存储**：除了数据本身，仪表的状态信息也会被记录，以便于状态的追踪和回溯。
6. **仪表控制参数更改**：通过网站界面，您可以远程调整仪表的控制参数，实现灵活的远程管理。

我正致力于扩展更多功能，未来计划实现的功能包括：

- **基于深度学习的特定物体识别**：利用最新的AI技术，识别并分析仪表图像中的特定对象。
- **基于文档信息的报警控制**：通过分析相关文档和信息，智能生成报警控制策略。
- **基于数据库数据的建模和分析**：对存储的大量数据进行深入分析，提取有价值的信息，支持决策制定。
- **更多控制算法和检测算法**：利用更多研究出的新控制算法、检测算法来进行运行实验。
- **对控制流程和算法的一些解释**：说明书。

请注意：由于作者即将外出学习，仪表没有经过稳定性检测，因此网站的仪表信息更新将于2024/2/10-2024/2/17(共7天内)暂时中断。作者对由此带来的不便深表歉意，并感谢您的理解和支持。
"""

# 将提示翻译成英文
website_prompt_english = """
    **A Message from the Author:**
    Welcome to my Cloud-based Instrumentation Dashboard Example Website. This site offers a set of \
    features for real-time monitoring and management of instrument data. Currently implemented features include:
    1. **Instrument Log Charts**: View historical records and trends of instrument \
    data with support for various chart displays.
    2. **Data Reading**: Real-time data reading from instruments, \
    ensuring you have immediate access to the latest information.
    3. **Status Detection**: Monitor the current status of instruments, \
    including but not limited to on/off status, performance metrics, etc.
    4. **Database Storage**: All instrument data are securely stored in the \
    cloud database, facilitating the query and analysis of historical data.
    5. **Instrument Status Storage**: In addition to the data itself, the status \
    information of the instruments is also recorded for tracking and retrospective purposes.
    6. **Instrument Control Parameter Changes**: Through the website interface, \
    you can remotely adjust the control parameters of the instruments for flexible remote management.

    I am committed to expanding more features, with future planned functionalities including:

    - **Specific Object Recognition Based on Deep Learning**: Utilizing the latest \
    AI technology to identify and analyze specific objects in instrument images.
    - **Alarm Control Based on Document Information**: Intelligently generate \
    alarm control strategies by analyzing related documents and information.
    - **Modeling and Analysis Based on Database Data**: Perform in-depth analysis \
    on the stored vast amount of data to extract valuable information to support decision-making.
    - **More Control and Detection Algorithms**: Utilize newly developed control and \
    detection algorithms for experimental operations.
    - **Explanations of Control Processes and Algorithms**: Manuals providing explanations.
    Please note: Due to the author's forthcoming study trip and the instruments \
    not undergoing stability testing, the update of instrument information on the \
    website will be temporarily interrupted from 2024/2/10 to 2024/2/17 (for 7 days).\
     The author deeply apologizes for any inconvenience this may cause and appreciates \
     your understanding and support.
"""