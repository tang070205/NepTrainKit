


### 1.操作界面

如图所示，该软件的整体操作界面主要包括工具栏、结果可视化区、结构展示区、信息显示区和工作路径显示区。

<img alt="操作界面" height="100" src="./image/操作界面.png" width="100"/>

### 2、文件导入

用户可以通过以下两种方式导入文件：

- 点击菜单左上角的导入按钮<img src="../src/NepTrainKit/src/images/open.svg" alt="open" style="zoom: 50%;" />导入路径。
- 将文件直接拖拽到软件界面中进行导入。

> [!NOTE]
>
> （1）请确保 NepTrainkit 的工作路径中不包含中文字符，否则可能导致程序无法正常显示。
>
> （2）为了保证 NepTrainkit 正常显示图像，至少需要提供 **nep.txt** 和 **train.xyz** 两个文件。

### 3、工具栏

在绘图工具栏中，我们集成了还原、缩放、选中编辑、撤销、删除等功能按钮，用户可以通过这些功能对图像进行一些基本操作。请注意，这些操作工具仅对主图有效。

<img alt="工具栏" height="200" src="./image/工具栏.png" width="200"/>

<img src="../src/NepTrainKit/src/images/init.svg" alt="init" style="zoom:20%;" width="20" height="20"/> 还原工具：将图片恢复到初始状态，清除所有已做的修改。

<img src="../src/NepTrainKit/src/images/pan.svg" alt="pan" style="zoom:50%;" width="20" height="20"/> 缩放工具：可以拖动图像的坐标轴或对图像进行缩放，调整视图位置。

<img src="../src/NepTrainKit/src/images/find_max.svg" alt="find_max" style="zoom:50%;" width="20" height="20"/> 误差最大点选择工具：自动识别指定数量的误差最大点，便于用户进行处理。

<img src="../src/NepTrainKit/src/images/sparse.svg" alt="sparse" style="zoom:50%;" width="20" height="20"/> 最远点采样工具：用户可自行设置训练集最大数量和最小取样距离来筛选结构。           

<img src="../src/NepTrainKit/src/images/pen.svg" alt="pen" style="zoom:50%;" width="20" height="20"/> 选中编辑工具：鼠标左键框选或直接选中结构，鼠标右键可取消选中。

<img src="../src/NepTrainKit/src/images/revoke.svg" alt="revoke" style="zoom:50%;" width="20" height="20"/> 撤销工具：如果误删或误操作，可以使用撤销功能恢复之前的状态，支持连续多次撤销。

<img src="../src/NepTrainKit/src/images/delete.svg" alt="delete" style="zoom:50%;" width="20" height="20"/> 删除工具：移除选中点所对应的结构。

### 4、结果可视化和结构展示

- 在结果可视化区域共有五个子图，展示了数据集的描述符、能量、力、压力和位力信息。我们采用**pyqtgraph**库来封装绘图功能，同时五个子图都支持通过双击操作切换为主图。

- 通过点击主图中的数据点，便可以在右侧展示区得到相应的晶体结构，晶体结构中的原子大小和颜色分别依据原子半径和CPK配色方案来设定。

 <img src="./image/可视化.png" alt="可视化" style="zoom: 80%;" />

**绘图细节：**在绘图过程中，**能量**、**力**、**压力**和**位力**数据均从工作路径中的 NEP 输出文件中读取。对于**描述符的投影**，我们使用 NEP_CPU 获取每个原子的描述符，计算其平均值作为结构描述符。然后，采用主成分分析（PCA）方法将结构描述符投影到二维空间，以便于可视化展示。

### 5、信息显示区

在右侧文本信息区显示了xyz文件的信息，并在下方给出了当前结构在原始文件中的帧数。默认情况下，点击任一子图中的数据点，显示区将同步展示所选结构的详细信息。

<img src="./image/信息显示.png" alt="信息显示" style="zoom:80%;" />

### 6、结果导出

操作完成后，可以点击导出按钮<img src=".../src/NepTrainKit/src/images/save.svg" alt="save" style="zoom:50%;" />将结果导出为两个文件：

- **export_remove_model.xyz**：包含已删除结构的信息。

- **export_good_model.xyz**：包含剩余结构的信息。