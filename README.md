


## 环境安装
```bash

conda create -n NepTrainKit -n python=3.10
conda activate NepTrainKit
pip install -r requirements.txt 

```


## 打包
```bash
python -m nuitka --mingw64   --windows-console-mode=disable    --standalone  --warn-implicit-exceptions  --warn-unusual-code --show-progress   --plugin-enable=pyside6 --plugin-enable=pylint-warnings     --windows-icon-from-ico=./src/images/logo.svg --output-dir=out main.py

```
 