# 仓库操作记录

更新：2026-09-08

前轮创建文件曾返回403 Resource not accessible by integration。本轮重新实测成功，不再要求用户重复授权。

- 仓库：WangTianYuan/dota，公开仓库。
- main初始提交：5498d78e038b822c57215e7efde7e5c3ca65760c，仅基础README。
- 研究分支：kb/bootstrap。
- 工作方式：研究内容提交到分支，创建Pull Request；不自动合并到main。
- 推送权限以每次真实动作结果为准，不由用户admin字段替代。

## 用户操作

本轮不需要提供密码、Token或额外授权。研究PR可在Files changed审阅，再决定是否合并。合并前main只有初始化页属于正常现象。

若以后发生403，先确认连接所用GitHub账号及该App是否仍选择dota仓库，再按实际错误检查文件内容/PR写入权限；分支保护冲突与没有仓库授权是两类问题。不要在聊天中粘贴访问令牌。
