# Process Flow Visualizer

独立静态页，展示 Assistant ↔ Sub-agent ↔ Workspace 的典型 I/O 形状。示例请求体写死在 `app.js`，无表单。

## Run

```bash
cd process-flow-visualizer
python3 -m http.server 3030
```

打开 `http://localhost:3030`。
