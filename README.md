# Knowledge Graph

An interactive, force-directed graph that visualizes your Notion knowledge base — topics, concepts, and their prerequisite relationships — rendered on an HTML5 Canvas and embedded directly into Notion.

## Features

- **Canvas rendering** — single flat draw call via `force-graph`; no SVG DOM bloat, no CPU heat at scale
- **Directional arrows** — prerequisite → concept relationships rendered with arrowheads
- **Tag-based coloring** — nodes colored by category using a decoupled theme file
- **Draggable nodes** — pin any node by dragging; physics continues for the rest
- **Hover tooltips** — node name and tag on hover
- **Manual refresh** — floating button re-fetches `graph_data.json` with a cache-buster; no full page reload
- **$0/month** — GitHub Pages hosting + GitHub Actions on `workflow_dispatch`

## Stack

| Layer | Technology |
|---|---|
| Rendering | [`force-graph`](https://github.com/vasturiano/force-graph) (Canvas) |
| Theme | Decoupled `theme.js` config object |
| Data pipeline | Python 3 + `requests` (Notion API v1) |
| Hosting | GitHub Pages |
| Automation | GitHub Actions (`workflow_dispatch`) |
| Data source | Notion Internal Integration |

## Repository Structure

```
├── index.html                          # Graph UI — canvas renderer + refresh button
├── theme.js                            # Visual config (colors, sizes, fonts)
├── graph_data.json                     # Static data file served to the frontend
├── build_graph.py                      # Notion API → graph_data.json extractor
└── .github/workflows/update_graph.yml  # Manual trigger workflow
```

## Setup

### 1. Notion Integration

1. Go to [Notion Developers](https://www.notion.so/my-integrations) and create a new **Internal Integration**.
2. Copy the **Integration Secret**.
3. Open your Knowledge Base database in Notion → `...` → **Connections** → connect your integration.
4. Copy the **Database ID** from the page URL (32-character string before `?v=`).

### 2. GitHub Secrets

In your repository: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|---|---|
| `NOTION_TOKEN` | Your Notion Integration Secret |
| `NOTION_DATABASE_ID` | Your 32-character database ID |

### 3. Property Names

Open `build_graph.py` and confirm these match your Notion database column names exactly:

```python
PROP_NAME          = "Name"           # Title column
PROP_TAG           = "Tags"           # Select or Multi-select column
PROP_PREREQUISITES = "Prerequisites"  # Relation column
```

### 4. GitHub Pages

**Settings → Pages → Source: Deploy from branch `main`, folder `/`**

Your graph will be live at `https://<username>.github.io/<repo>/`.

### 5. Embed in Notion

In any Notion page, type `/embed`, paste your GitHub Pages URL, and resize the block.

## Updating the Graph

1. Add or update concepts and prerequisite links in your Notion database.
2. Go to the **Actions** tab in your GitHub repository.
3. Select **Update Knowledge Graph** → **Run workflow**.
4. Once the run completes, click **Refresh Graph** in your Notion embed.

## Customization

All visual configuration lives in `theme.js`. No rendering logic needs to change.

```js
const GraphTheme = {
    canvas: {
        background: "#f8f9fa",
    },
    nodes: {
        defaultColor: "#e2e8f0",
        tagColors: {
            "Linear Algebra":     "#a8d8ea",
            "Information Theory": "#aa96da",
            "Optimization":       "#fcbad3",
            "Practice":           "#b5ead7"
        },
        textColor: "#374151",
    },
    links: {
        color: "#cbd5e1",
        arrowLength: 6,
    }
};
```

To add a new tag color, add an entry to `tagColors` matching the exact tag name used in Notion.

## License

MIT
