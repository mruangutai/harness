// Route `/?window=<w>` — the aggregate level of DESIGN.md §C-1's drill.
//
// Everything on this page is scoped to the window in the URL EXCEPT the trend
// section, which deliberately renders one panel per window token. That is a
// prototype-only affordance and the README says so: DESIGN.md's product shows
// one trend region for the selected window, but S-1 and S-2 are told apart by
// whether AXES ARE DRAWN, and a reviewer cannot compare two states they have to
// navigate between. Putting the 30d panel (S-1, no axes) beside the 90d and all
// panels (S-2, axes and a broken line) is what makes that judgement possible in
// one screenshot.

import {HStack, Link, Text, VStack} from '@astryxdesign/core';
import {Link as RouterLink} from '@tanstack/react-router';
import {T, TYPE} from '../theme.js';
import {PanelHeader} from '../components/primitives.jsx';
import {KpiTiles} from '../components/KpiTiles.jsx';
import {TrendPanel} from '../components/TrendPanel.jsx';
import {GradingPanel} from '../components/GradingPanel.jsx';
import {GapPair} from '../components/GapPair.jsx';
import {Shell} from '../components/Shell.jsx';
import {windowPoints} from '../lib/series.js';
import {WINDOW_TOKENS} from '../fixture.js';

export function Aggregate({windowToken}) {
  return (
    <Shell windowToken={windowToken}>
      <VStack gap={6}>
        <VStack gap={3}>
          <PanelHeader
            title="Six KPIs for the window"
            sub="a 40pt headline figure, a one-line denominator, and — for throughput, touchpoints and code grading — an 8-point sparkline. A figure never appears without its denominator or its unit."
          />
          <KpiTiles windowToken={windowToken} />
          <HStack gap={2} align="baseline" wrap="wrap">
            <Text color="secondary" style={{fontSize: TYPE.tick}}>
              Any tile drills to the rows behind it:
            </Text>
            <Link as={RouterLink} to="/features" search={{window: windowToken, sort: 'grading'}}>
              the 8 feature rows, sorted by code grading
            </Link>
          </HStack>
        </VStack>

        <VStack gap={3}>
          <PanelHeader
            title="Trend region, one panel per window token"
            sub="30d holds no ship records, so its region is replaced outright. 90d and all draw axes. That difference — axes or no axes — is how S-1 and S-2 are told apart."
          />
          {WINDOW_TOKENS.map((token) => (
            <TrendPanel
              key={token}
              windowToken={token}
              points={windowPoints(token)}
              isSelected={token === windowToken}
            />
          ))}
          <Text color="secondary" style={{fontSize: TYPE.tick, color: T.textMuted}}>
            Three series, one shared x axis, a y scale each: hours, a count and a 1–5 grade share do
            not share a scale. Series identity is carried by dash pattern, marker shape and a direct
            end-of-line label, never by hue alone.
          </Text>
        </VStack>

        <GradingPanel windowToken={windowToken} />

        <GapPair />
      </VStack>
    </Shell>
  );
}
