# サンプルの動かし方

## Install 

### 1. pigpioの設定

```
# `pigpio`パッケージのインストール
sudo apt install pigpio

# pigpioサービスの自動起動設定
sudo systemctl enable pigpiod.service
sudo systemctl start pigpiod.service
```


### 2. `uv`のインストールと設定

```
curl -LsSf https://astral.sh/uv/install.sh | sh

# PATHの設定
# 以下を、.bashrc, .zshrcなどに登録することが望ましい。
export PATH=$PATH:~/.local/bin
```

## 3. 'piservo0'のダウンロードとインストール

```
git clone https://github.com/ytani01/piservo0.git


```


