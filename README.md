# ZZU-Electricity
自用宿舍用电记录

## Repository Secrets 配置
需要在GitHub Secrets中添加以下变量
|   Repository Secrets   | Description |
| ----------- | ----------- |
| `EMAIL` | GitHub邮箱 |
| `GH_USERNAME` | GitHub用户名 |
| `GH_ACCESS_TOKEN` | 有`repo`权限的 GitHub Access Token |
| `ZZU_CONFIG` | 用于配置`ZZU-API`，详情请看[ZZU-API](https://github.com/TorCroft/ZZU-API) |
| `ZZU_NOTIFIER` | Onepush的推送配置，格式是 `{notifier}#{key}`, 例如iOS Bark：`bark#your_bark_key`|
