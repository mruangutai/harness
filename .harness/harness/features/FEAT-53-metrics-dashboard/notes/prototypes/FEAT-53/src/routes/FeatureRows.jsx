// Route `/features?window=<w>&sort=<kpi>` — the rows behind an aggregate.
// Step two of the drill SC-11 hand-tests: tile -> /features?sort=<kpi> ->
// /features/$featureId. Three routes, no server restart, no file edit, and no
// modal at any depth, so every view is linkable, reloadable and
// back-button-safe.

import {Text, VStack} from '@astryxdesign/core';
import {TYPE} from '../theme.js';
import {PanelHeader} from '../components/primitives.jsx';
import {FeatureTable} from '../components/FeatureTable.jsx';
import {Shell} from '../components/Shell.jsx';
import {KPIS} from '../fixture.js';

export function FeatureRows({windowToken, sortKey}) {
  const kpi = KPIS.find((k) => k.key === sortKey);
  return (
    <Shell windowToken={windowToken}>
      <VStack gap={3}>
        <PanelHeader
          title="One row per feature, all six KPIs as columns"
          sub={`sorted by ${kpi ? kpi.title : 'throughput'} — the KPI drilled from, carried in the URL as ?sort=`}
        />
        <FeatureTable windowToken={windowToken} sortKey={sortKey} />
        <Text color="secondary" style={{fontSize: TYPE.tick}}>
          A feature name opens that feature. The window travels with it, so the drill never resets
          what was selected.
        </Text>
      </VStack>
    </Shell>
  );
}
