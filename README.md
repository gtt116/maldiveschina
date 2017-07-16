## Usage

它会将所有在 http://www.maldiveschina.com/ 网站中列出的岛屿输出到本地表格。


```bash
git clone https://github.com/gtt116/maldiveschina
cd maldiveschina
pip install -r requirements.txt
python main.py  # maldiveschina.csv 文件将会被刷新
csvtotable maldiveschina.csv  maldiveschina.html  # maldiveschina.html 会被刷新

python -mSimpleHTTPServer   # 访问这台机器的8000端口即可
```
