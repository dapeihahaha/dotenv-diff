# dotenv-diff

[![CI](https://github.com/dapeihahaha/dotenv-diff/actions/workflows/ci.yml/badge.svg)](https://github.com/dapeihahaha/dotenv-diff/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Compare your `.env` against `.env.example` and catch **missing**, **extra**, **empty**, and **duplicate** variables — locally or in CI. Zero dependencies.

[中文说明](#中文说明)

```console
$ dotenv-diff
Missing: 2
  - DATABASE_URL
  - STRIPE_KEY
Empty: 1
  - SENTRY_DSN
✗ .env does not match .env.example
```

## Install

```bash
pip install git+https://github.com/dapeihahaha/dotenv-diff
```

Requires Python 3.9+.

## Usage

```bash
dotenv-diff                       # compares .env with .env.example
dotenv-diff .env.local .env.example
dotenv-diff --strict              # also fail on keys not in the template
dotenv-diff --allow-empty         # empty values are OK
dotenv-diff --ignore DEBUG --ignore LOCAL_ONLY
dotenv-diff --format json         # machine-readable output
```

| Exit code | Meaning |
|-----------|---------|
| `0` | Files match |
| `1` | Problems found (missing keys, empty values, or extra keys with `--strict`) |
| `2` | Usage error: file not found or unparsable |

Duplicate keys are always reported as a warning and never change the exit code.

### In CI (GitHub Actions)

```yaml
- uses: actions/checkout@v4
- uses: dapeihahaha/dotenv-diff@v0.2.0
  with:
    env: .env.ci              # default: .env
    template: .env.example    # default: .env.example
    args: --strict            # any extra CLI flags
```

The action needs only the Python that GitHub-hosted runners already have; nothing is installed.

### Supported syntax

```bash
# comments and blank lines
KEY=value
export KEY=value
KEY="double quoted, supports \n escapes"
KEY='single quoted # not a comment'
KEY=value # inline comment
KEY=
```

## Use as a library

```python
from dotenv_diff import compare, parse_file

result = compare(parse_file(".env"), parse_file(".env.example"))
print(result.missing, result.extra, result.empty)
```

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)

---

## 中文说明

`dotenv-diff` 用来对比 `.env` 与 `.env.example`，找出**缺失**、**多余**、**为空**和**重复**的环境变量。无第三方依赖，适合在本地或 CI 中使用。

```bash
pip install git+https://github.com/dapeihahaha/dotenv-diff
dotenv-diff                 # 对比 .env 与 .env.example
dotenv-diff --strict        # 模板中没有的变量也视为错误
dotenv-diff --format json   # 输出 JSON
```

退出码：`0` 一致，`1` 发现问题，`2` 文件不存在或格式错误。

在 GitHub Actions 中使用：

```yaml
- uses: dapeihahaha/dotenv-diff@v0.2.0
  with:
    env: .env.ci
    args: --strict
```
