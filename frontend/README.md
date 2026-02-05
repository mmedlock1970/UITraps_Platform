# UI Traps Analyzer React Component

Embeddable React component for analyzing UI designs using the UI Tenets & Traps framework.

## Installation

```bash
npm install @uitraps/analyzer-react
```

## Quick Start

```tsx
import { UITrapsAnalyzer } from '@uitraps/analyzer-react';
import '@uitraps/analyzer-react/styles.css';

function App() {
  return (
    <UITrapsAnalyzer
      apiEndpoint="https://api.uitraps.com"
      apiKey="your-api-key"
      theme="light"
      onAnalysisComplete={(result) => {
        console.log('Analysis complete:', result);
      }}
    />
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `apiEndpoint` | `string` | required | Backend API URL |
| `apiKey` | `string` | required | Your API key |
| `theme` | `'light' \| 'dark'` | `'light'` | Color theme |
| `showUsageInfo` | `boolean` | `false` | Show remaining quota |
| `showStatistics` | `boolean` | `true` | Show issue counts |
| `initialUsers` | `string` | `''` | Pre-fill users field |
| `initialTasks` | `string` | `''` | Pre-fill tasks field |
| `initialFormat` | `string` | `''` | Pre-fill format field |
| `onAnalysisStart` | `() => void` | - | Callback when analysis starts |
| `onAnalysisComplete` | `(result) => void` | - | Callback on success |
| `onAnalysisError` | `(error) => void` | - | Callback on error |
| `timeout` | `number` | `120000` | Request timeout in ms |
| `className` | `string` | - | Additional CSS class |
| `style` | `CSSProperties` | - | Inline styles |

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Build as library
npm run build:lib
```

## Embedding in Your Site

### Option 1: React App

```tsx
import { UITrapsAnalyzer } from '@uitraps/analyzer-react';
import '@uitraps/analyzer-react/styles.css';

<UITrapsAnalyzer apiEndpoint={API_URL} apiKey={apiKey} />
```

### Option 2: Script Tag (UMD)

```html
<link rel="stylesheet" href="path/to/uitraps-analyzer.css">
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="path/to/uitraps-analyzer.umd.js"></script>

<div id="analyzer"></div>
<script>
  const root = ReactDOM.createRoot(document.getElementById('analyzer'));
  root.render(
    React.createElement(UITrapsAnalyzer.UITrapsAnalyzer, {
      apiEndpoint: 'https://api.uitraps.com',
      apiKey: 'your-api-key'
    })
  );
</script>
```

## Customization

### CSS Variables

Override CSS custom properties to customize the appearance:

```css
.uitraps-analyzer {
  --uitraps-primary: #your-brand-color;
  --uitraps-border-radius: 4px;
  --uitraps-font-family: 'Your Font', sans-serif;
}
```

### Individual Components

Import individual components for advanced customization:

```tsx
import {
  FileUpload,
  ContextInputs,
  AnalysisProgress,
  ReportViewer,
  useAnalyzer,
} from '@uitraps/analyzer-react';
```

## API Integration

The component communicates with the backend via:

- `POST /analyze` - Submit image and context for analysis
- `GET /usage` - Check remaining quota
- `GET /health` - Health check

See the main project documentation for API details.
