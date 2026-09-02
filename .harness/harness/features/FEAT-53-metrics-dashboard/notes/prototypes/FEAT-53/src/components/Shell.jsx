// The page shell: the synthetic-fixture banner, the window control, the theme
// toggle, and the breadcrumb that makes the three-route drill legible.
//
// DESIGN.md §C-1's contract, and the thing SC-11 hand-tests: the selected
// window and the selected feature live ONLY in the URL. Nothing here holds
// either in local state — the control reads the URL and writes the URL, so a
// reload, a back-navigation, or a paste of the URL into a second tab keeps
// both. The tokens are named (30d, 90d, all) rather than a date pair, so a URL
// still means something when it is read a week later.

import {
  Banner,
  Divider,
  HStack,
  Link,
  SegmentedControl,
  SegmentedControlItem,
  Text,
  VStack,
} from '@astryxdesign/core';
import {Link as RouterLink, useNavigate, useRouterState} from '@tanstack/react-router';
import {RADIUS, SIZE, T, TYPE} from '../theme.js';
import {THEME_MODES, useThemeMode} from '../lib/themeMode.jsx';
import {PROJECT, WINDOWS, WINDOW_TOKENS} from '../fixture.js';

function WindowControl({windowToken}) {
  const navigate = useNavigate();
  const pathname = useRouterState({select: (s) => s.location.pathname});

  return (
    <VStack gap={1}>
      <Text weight="medium" style={{fontSize: TYPE.tick}}>
        Window — lives in the URL as ?window=
      </Text>
      <SegmentedControl
        label="Time window"
        value={windowToken}
        onChange={(value) => navigate({to: pathname, search: (prev) => ({...prev, window: value})})}
      >
        {WINDOW_TOKENS.map((token) => (
          <SegmentedControlItem key={token} value={token} label={token} />
        ))}
      </SegmentedControl>
      <Text color="secondary" style={{fontSize: TYPE.tick}}>
        {`${windowToken} · ${WINDOWS[windowToken].label} · ${WINDOWS[windowToken].shipRecords} ship records`}
      </Text>
    </VStack>
  );
}

function ThemeControl() {
  const {mode, setMode} = useThemeMode();
  return (
    <VStack gap={1}>
      <Text weight="medium" style={{fontSize: TYPE.tick}}>
        Theme — an explicit control, defaulting to the OS preference
      </Text>
      <SegmentedControl label="Theme" value={mode} onChange={setMode}>
        {THEME_MODES.map((m) => (
          <SegmentedControlItem key={m} value={m} label={m} />
        ))}
      </SegmentedControl>
      <Text color="secondary" style={{fontSize: TYPE.tick}}>
        both themes ship from one defineTheme [light, dark] tuple
      </Text>
    </VStack>
  );
}

function Breadcrumb({windowToken, feature}) {
  return (
    <HStack gap={2} align="baseline" wrap="wrap">
      <Link as={RouterLink} to="/" search={{window: windowToken}}>
        aggregate
      </Link>
      <Text color="secondary" style={{fontSize: TYPE.tick}}>
        {'\u203a'}
      </Text>
      <Link as={RouterLink} to="/features" search={{window: windowToken}}>
        feature rows
      </Link>
      <Text color="secondary" style={{fontSize: TYPE.tick}}>
        {'\u203a'}
      </Text>
      <Text color={feature ? 'primary' : 'secondary'} style={{fontSize: TYPE.tick}}>
        {feature ? `${feature.id} · ${feature.name}` : 'one feature'}
      </Text>
    </HStack>
  );
}

export function Shell({windowToken, feature, children}) {
  return (
    <VStack
      gap={4}
      padding={6}
      maxWidth={SIZE.container}
      style={{marginInline: 'auto', backgroundColor: T.bg, minHeight: '100vh'}}
    >
      <Banner
        variant="warning"
        title={PROJECT.banner}
        description={`Project "${PROJECT.label}" is fictional. Every figure below is hand-authored. There is no fetch, no filesystem read, no git and no code grader anywhere in this build.`}
      />

      <HStack gap={4} wrap="wrap" justify="space-between" align="end">
        <VStack gap={1}>
          <Text as="h1" weight="semibold" style={{fontSize: TYPE.stateHead}}>
            Metrics dashboard — FEAT-53 design prototype
          </Text>
          <Breadcrumb windowToken={windowToken} feature={feature} />
        </VStack>
        <HStack gap={4} wrap="wrap" align="start">
          <WindowControl windowToken={windowToken} />
          <ThemeControl />
        </HStack>
      </HStack>

      <Divider variant="subtle" />

      {children}

      <Divider variant="subtle" />
      <VStack gap={1} padding={3} style={{borderRadius: RADIUS.card, backgroundColor: T.surface}}>
        <Text weight="medium" style={{fontSize: TYPE.tick}}>
          The four honest-gap states, and where to find each one on this page
        </Text>
        <Text color="secondary" style={{fontSize: TYPE.tick}}>
          S-1 the 30d trend region and the 30d tile sparklines — the region is replaced, no axes at
          all. S-2 the 90d and all trend regions — axes drawn, the line breaks, hatched trend cells
          in the table. S-3 beneath the histogram in the grading panel. S-4 the pair panel, and
          every unavailable cell in the table.
        </Text>
      </VStack>
    </VStack>
  );
}
