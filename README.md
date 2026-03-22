## Pytest + Requests 接口自动化测试框架（POM/API Object）

### 目录结构

- `api/`: 接口封装（按业务域拆分，一个类一组接口）
- `testcases/`: 测试用例
- `data/`: 测试数据（JSON / Excel）
- `utils/`: 工具类（配置、日志、断言、数据驱动、提取、token）
- `config/`: 配置文件（多环境）
- `reports/`: 测试报告与运行日志

### 功能点对应关系

- **Page Object 模型**：在接口测试里通常叫 **API Object**（和 POM 思路一致：把接口调用封装成对象方法），示例见 `api/httpbin_api.py`
- **接口关联 / token 自动管理**：`utils/token_manager.py` + `api/base_api.py` 自动注入 Header（`Authorization: Bearer <token>`）
- **参数化测试（Excel/JSON）**：`utils/data_driver.py`（JSON/Excel 两种入口），示例用例见 `testcases/`
- **多环境切换**：`config/config.yaml`，通过环境变量 `ENV=dev/test/prod`
- **HTML 报告**：pytest-html（默认输出 `reports/pytest_report.html`）
- **失败自动重跑**：pytest-rerunfailures（默认 rerun 1 次，可在 `pytest.ini` 改）
- **日志**：`utils/logger.py` 输出到控制台 + `reports/run.log`

### 1) 安装依赖

在项目根目录执行：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) 配置多环境

默认读取 `config/config.yaml`：

- **dev/test/prod**：配置 `base_url/timeout/verify_ssl`
- **auth.token_header/token_prefix**：token 注入策略

切换环境方式（示例切 test）：

```bash
ENV=test pytest
```

### 3) 运行用例与生成报告

直接运行（会生成 HTML 报告）：

```bash
pytest
```

报告位置：

- `reports/pytest_report.html`
- `reports/run.log`

### 4) JSON 数据驱动用法

示例数据：`data/httpbin_cases.json`（list case）

示例用例：`testcases/test_httpbin_demo.py`

核心写法：

```python
@data_driver(json_file="data/xxx.json", key="cases", argnames="case")
def test_xxx(case):
    ...
```

### 5) Excel 数据驱动用法

由于 `xlsx` 是二进制文件，这里用脚本生成示例 Excel（一次执行即可）。

生成 Excel：

```bash
python scripts/generate_example_excel.py
```

生成后会得到：`data/httpbin_cases.xlsx`

示例用例：`testcases/test_httpbin_excel_demo.py`

Excel 约定：

- 第一行：表头（字段名）
- 第二行起：数据行
- 单元格若是 JSON 字符串（如 `{"a":1}`），用例里可自行 `json.loads` 解析（示例已演示）

### 6) token 自动管理（接口关联）怎么接入你自己的项目

当前框架已经具备两件事：

1. **Token 存储**：`token_manager.set(token)`
2. **自动注入 Header**：所有 `BaseRequest.request(...)` 会自动把 token 写进 Header

你只需要在“登录接口封装”里做一次提取并写入：

```python
token = extract_jsonpath(result.json, "$.token")
token_manager.set(token)
```

建议做法：

- 新建 `api/auth_api.py`，封装 `login()`，拿到 token 后 `token_manager.set(...)`
- 在 `conftest.py` 里加一个 `session` 级别 fixture（例如 `autouse=True`）先登录再跑用例

### 7) 扩展建议（你接下来可按需加）

- Allure 报告：加依赖 `allure-pytest`，并在命令里输出 `--alluredir=reports/allure-results`
- 统一响应断言、schema 校验：在 `utils/assertions.py` 里继续扩展
- 更强的提取/关联：用 `jsonpath-ng` 做提取已覆盖 80% 场景；也可补 “从 Header/Cookie 提取”

### 8) 用于测试 GitHub API（已提供示例）

#### 8.1 切换到 GitHub 环境（真实环境）

关闭本地 Mock，并切换环境到 `github`：

```bash
USE_LOCAL_SERVER=0 ENV=github pytest -m smoke
```

#### 8.2 配置 Token（可选但推荐）

GitHub 访问 `/user` 需要鉴权。推荐使用环境变量传入（不要写进代码/文件）：

```bash
export GITHUB_TOKEN="你的 GitHub Token"
```

可选：指定你要测的用户名（用于公共端点 `/users/{username}/repos`）：

```bash
export GITHUB_USERNAME="octocat"
```

#### 8.3 示例用例

- `testcases/test_github_api_demo.py`
  - `test_github_rate_limit`：无需 token
  - `test_github_user_requires_token`：需要 `GITHUB_TOKEN`，否则自动 skip
  - `test_github_list_user_repos`：无需 token

### 9) 测一个真实公网接口（百度 / 千问）

> 注意：如果你在某些受限环境（例如沙箱/内网）运行，可能无法访问公网域名；这不是框架问题。

#### 9.1 百度（无需密钥）

用例：`testcases/test_real_api_demo.py::test_baidu_homepage`

运行：

```bash
USE_LOCAL_SERVER=0 pytest -q testcases/test_real_api_demo.py -k baidu
```

#### 9.2 通义千问 Qwen（需要密钥）

用例：`testcases/test_real_api_demo.py::test_qwen_chat_completion`

准备环境变量（推荐只放到环境变量，不要写进代码/文件）：

```bash
export DASHSCOPE_API_KEY="你的 DashScope API Key"
```

运行：

```bash
USE_LOCAL_SERVER=0 pytest -q testcases/test_real_api_demo.py -k qwen
```

---

## Kong Gateway + Cypress

包含两类用例：

1. **`cypress/e2e/kong_admin_api_smoke.cy.js`** — `cy.request` 访问 Admin API **`:8001`**，快速确认网关已就绪。  
2. **`cypress/e2e/kong_service_route.cy.js`** — **Kong Manager UI（`:8002`）**：从零创建 **Gateway Service**，再创建 **Route**（满足「Basic test actions」类要求）。

### Setup（与作业要求一致）

按顺序完成以下步骤即可满足 **Setup** 检查项：

| 步骤 | 说明 |
|------|------|
| 1. 获取 Compose 文件 | 本仓库根目录已包含 **`docker-compose.yml`**（若作业单独提供文件，将其放到项目根目录或替换该文件）。 |
| 2. 进入目录 | 在终端 **`cd`** 到 **`docker-compose.yml` 所在目录**（本仓库为项目根目录）。 |
| 3. 启动容器 | 启动前请先准备本地环境变量（创建 `.env` 或手动导出 `KONG_PASSWORD` / `POSTGRES_PASSWORD`），然后执行 **`docker-compose up -d`**。若本机为 Docker Compose V2，也可使用 **`docker compose up -d`**（无连字符）。 |
| 4. 打开 Kong Manager | 在浏览器访问 **`http://localhost:8002/`**。 |
| 5. 确认 UI 可访问 | 应能进入 **Kong Gateway UI（Kong Manager）**。页面顶部出现 **“No valid Kong Enterprise license configured”** 之类提示 **属于预期**，说明环境正确。 |

`docker-compose.yml` 中已配置 **`KONG_ADMIN_GUI_LISTEN`** 监听 **8002**，与上述 URL 一致。

如果你要把该仓库公开并依赖 **GitHub Actions** 自动跑 Cypress，请在仓库的 Settings 里配置以下 **Secrets**：

- `KONG_USERNAME`：Kong Manager UI 登录用户名
- `KONG_PASSWORD`：Kong Manager UI 登录密码（同时也用于初始化 Kong 管理口）
- `POSTGRES_PASSWORD`：Postgres 的密码（用于 kong-ee-database）

CI 会把这些值注入到 `docker compose up -d` 和 Cypress 运行环境中。

### 运行前置条件

- **Docker** + Compose；**Node.js 18+**（建议 20）。

### 本地运行（Cypress）

1. 若尚未启动 Kong，先在 Compose 目录执行（同 Setup 步骤 3；确保已设置 `.env`/环境变量）：

```bash
docker compose up -d
```

2. 安装依赖并运行 **全部** Cypress 用例

```bash
npm install
npm run cypress:run
```

只跑 UI 用例：

```bash
npx cypress run --spec cypress/e2e/kong_service_route.cy.js
```

只跑 Admin API 冒烟：

```bash
npx cypress run --spec cypress/e2e/kong_admin_api_smoke.cy.js
```

环境变量（可选，与 `docker-compose.yml` 中 `KONG_PASSWORD` 等一致）：

```bash
export CYPRESS_BASE_URL="http://localhost:8002"
export CYPRESS_KONG_ADMIN_URL="http://localhost:8001"
export CYPRESS_KONG_USERNAME="YOUR_KONG_USERNAME"
export CYPRESS_KONG_PASSWORD="YOUR_KONG_PASSWORD"

# docker compose required variables (if you use docker-compose up locally):
export KONG_PASSWORD="YOUR_KONG_PASSWORD"
export POSTGRES_PASSWORD="YOUR_POSTGRES_PASSWORD"
```

3. 关闭 Kong：`docker compose down`

### 说明与取舍

- Kong Manager **无 Enterprise license** 时界面可能 **只读**，UI 创建用例会失败；若 Create 按钮不可点，会提前报错提示。可用手动验证横幅 + Admin API 冒烟证明环境正常。  
- **`trust_store_mac.cc ... Error parsing certificate`**：macOS 上 Electron 读取系统证书库时的常见噪音，**与用例失败无关**，可忽略。  
- **JUnit**：`cypress/results/junit-*.xml`。  
- **CI**：`.github/workflows/kong-manager-cypress.yml` 等待 **`:8001` 与 `:8002`** 均可访问后跑 `npm run test:ci`。

