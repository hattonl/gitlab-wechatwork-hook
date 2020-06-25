# 声明

这个脚本利用 gitlab webhook，从 gitlab 接收一些提交、合并等改动信息，并通过企业微信机器人实时提醒项目组的成员。

本项目主要参考了以下这个项目，在其基础上进行了修改，添加了所需要的功能。

- https://github.com/razius/github-webhook-handler

# 在本机运行
```shell
# 下载依赖
pip install -r requirements.txt
# 运行之，开放80端口
sudo -E python index.py 80
```
# 集群运行
在集群上执行已交给系统组，并采用docker镜像：docker.servername.ai:5000/projectx/gitlab-wechatwork-hook:v3（tag可能会随时更新，采用最新版即可）

# TODO

## 当前不足
docker镜像中直接打包了这份脚本的的代码，这将导致每次修改该脚本文件后还需要重新升级docker镜像。

## 改进方案
这份脚本中可能要修改可能有下面几个地方。
1. 关于gitlab传来的事件处理。当前只处理了merge事件，其他事件都没有进行处理，后期可能会随着需求进行添加。
2. 当前转发的企业微信只有AI_BOX这个组群的企业微信机器人。后期进行其他项目时，可能会建立新的群，要替换企业微信的转发地址。

解决：将运行环境和代码分离。运行环境几乎不会发生变化，每次改变的只有代码或者配置文件。代码放到gitlab上保存，运行环境在docker镜像中打包好。docker容器在启动时进行最近代码的拉取，考虑到容器将在集群上一直运行的情况，可以采用定时拉取，或者每次更新此脚本代码时通知docker容器更新代码或者配置。