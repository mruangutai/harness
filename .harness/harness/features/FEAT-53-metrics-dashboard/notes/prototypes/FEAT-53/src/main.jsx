import {createRoot} from 'react-dom/client';
import {RouterProvider} from '@tanstack/react-router';
import {Theme} from '@astryxdesign/core';
import '@astryxdesign/core/reset.css';
import '@astryxdesign/core/astryx.css';
import './layout.css';
import {metricsTheme} from './theme.js';
import {makeRouter} from './router.jsx';

createRoot(document.getElementById('root')).render(<Theme theme={metricsTheme} mode="dark"><RouterProvider router={makeRouter()}/></Theme>);
