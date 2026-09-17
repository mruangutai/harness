import { Stack, Text } from '@astryxdesign/core';
import { barY, defineChart, lineY } from '@tanstack/charts';
import { Chart } from '@tanstack/charts/react';
import { scaleBand, scaleLinear, scaleUtc } from 'd3-scale';

const GRADES = ['1', '2', '3', '4', '5'] as const;
const chartTextStyle = { fontFamily: 'var(--font-family-body)', fontSize: 'var(--text-supporting-size)' };

type Grade = (typeof GRADES)[number];
type GradeBin = { grade: Grade; count: number; atBarCount?: number };
type TrendPoint = { at: string | Date; value: number; featureId: string };
type TrendSeries = {
  id: string;
  label: string;
  unit: string;
  hue: string;
  dash: string;
  marker: 'circle' | 'square' | 'triangle';
  runs: readonly (readonly TrendPoint[])[];
};

export type HistogramProps = { bins: readonly GradeBin[] };
export type TimeSeriesProps = { series: readonly TrendSeries[] };
function gradeRows(bins: readonly GradeBin[]) {
  const byGrade: Partial<Record<Grade, GradeBin>> = {};
  for (const bin of bins) byGrade[bin.grade] = bin;
  return GRADES.map((grade) => {
    const bin = byGrade[grade];
    return {
      grade,
      count: bin?.count ?? 0,
      atBarCount: bin?.atBarCount ?? 0,
      fill: `var(--color-metrics-grade-${grade})`,
    };
  });
}

function marker(shape: TrendSeries['marker'], color: string, x: number, y: number) {
  if (shape === 'square') return <rect x={x - 4} y={y - 4} width="8" height="8" fill={color} />;
  if (shape === 'triangle') return <path d={`M ${x} ${y - 5} L ${x - 5} ${y + 4} L ${x + 5} ${y + 4} Z`} fill={color} />;
  return <circle cx={x} cy={y} r="4" fill={color} />;
}

function trendDefinition(series: TrendSeries) {
  const marks = series.runs.filter((run) => run.length > 0).map((run) => lineY(run.map((point) => ({ ...point, at: new Date(point.at) })), {
    x: 'at',
    y: 'value',
    stroke: series.hue,
    strokeWidth: 2,
    strokeDasharray: series.dash,
    points: true,
  }));
  return defineChart({
    marks,
    scales: { x: { scale: scaleUtc }, y: { scale: scaleLinear, nice: true } },
    keyboard: false,
    tooltip: false,
  });
}

function HistogramChart({ bins }: HistogramProps) {
  const rows = gradeRows(bins);
  const definition = defineChart({
    marks: [barY(rows, { x: 'grade', y: 'count', fill: 'fill', stroke: 'var(--color-metrics-unavailable-stroke)', strokeWidth: 1 })],
    scales: {
      x: { scale: () => scaleBand<string>().domain([...GRADES]).padding(0.16) },
      y: { scale: scaleLinear, nice: true },
    },
    keyboard: false,
    tooltip: false,
  });
  return <Stack gap={2} style={{ width: '100%' }}>
    <div aria-hidden="true" style={{ height: '280px', width: '100%' }}>
      <Chart ariaLabel="Grade distribution" definition={definition} height={280} />
    </div>
    <Stack direction="horizontal" justify="between">{rows.map((row) => <Text key={row.grade} type="supporting" style={chartTextStyle}>Grade {row.grade}: {row.count}</Text>)}</Stack>
  </Stack>;
}

function TrendPlot({ series }: { series: TrendSeries }) {
  const end = series.runs.at(-1)?.at(-1);
  return <Stack gap={1} style={{ width: '100%' }}>
    <Text type="supporting" style={{ color: series.hue }}>{series.label} · {series.unit}</Text>
    <div aria-hidden="true" style={{ height: '88px', width: '100%' }}>
      <Chart ariaLabel={`${series.label} over time`} definition={trendDefinition(series)} height={88} />
    </div>
    {end ? <svg aria-hidden="true" width="100%" height="20" viewBox="0 0 400 20" preserveAspectRatio="none">
      {marker(series.marker, series.hue, 8, 10)}
      <text x="18" y="14" fill={series.hue} style={chartTextStyle}>{series.label}: {end.value}</text>
    </svg> : null}
  </Stack>;
}

export function ShapeA({ bins }: HistogramProps) {
  return <section data-testid="chart-shape-a" aria-hidden="true"><HistogramChart bins={bins} /></section>;
}

export function ShapeB({ series }: TimeSeriesProps) {
  return <section data-testid="chart-shape-b" aria-hidden="true" style={{ height: '320px', width: '100%' }}><Stack gap={2}>{series.map((item) => <TrendPlot key={item.id} series={item} />)}</Stack></section>;
}
