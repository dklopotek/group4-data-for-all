# Mermaid Style Configuration

## CLI command pattern

```bash
mmdc -i input.mmd -o output.svg \
  --theme base \
  --backgroundColor transparent \
  --cssFile references/mermaid-custom.css
```

## Theme config (pass as --config)

Save as `mermaid-config.json`:

```json
{
  "theme": "base",
  "themeVariables": {
    "primaryColor": "#2d4a6b",
    "primaryTextColor": "#ffffff",
    "primaryBorderColor": "#1a3050",
    "lineColor": "#6b8caa",
    "secondaryColor": "#f0f4f8",
    "tertiaryColor": "#e8f0e8",
    "background": "#ffffff",
    "mainBkg": "#2d4a6b",
    "nodeBorder": "#1a3050",
    "clusterBkg": "#f0f4f8",
    "titleColor": "#1a3050",
    "edgeLabelBackground": "#ffffff",
    "fontFamily": "Helvetica Neue, Arial, sans-serif",
    "fontSize": "14px"
  }
}
```

Full command:
```bash
mmdc -i input.mmd -o output.svg --config references/mermaid-config.json
```

## Subgraph color overrides (for pipeline diagrams with sources/processing/output zones)

Add to `mermaid-custom.css`:

```css
/* Sources subgraph — cool blue */
.cluster:nth-child(1) rect {
  fill: #dbeafe !important;
  stroke: #3b82f6 !important;
}

/* Processing subgraph — warm amber */
.cluster:nth-child(2) rect {
  fill: #fef3c7 !important;
  stroke: #f59e0b !important;
}

/* Output subgraph — green */
.cluster:nth-child(3) rect {
  fill: #d1fae5 !important;
  stroke: #10b981 !important;
}

/* Node labels */
.node rect {
  rx: 6px;
  ry: 6px;
}

text {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 13px;
}
```

## Output sizing

For A3-equivalent SVG (good for print):
```bash
mmdc -i input.mmd -o output.svg --width 1587 --height 1122
```

For screen / presentation:
```bash
mmdc -i input.mmd -o output.svg --width 1920 --height 1080
```
