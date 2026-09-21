import { appendFileSync } from "node:fs";

const OUT = process.env.OMP_LINEAGE_PROBE_OUT;

type ProbeContext = {
	agentId?: string;
	parentAgentId?: string;
};

type ToolEvent = {
	toolName?: string;
};

type ProbeApi = {
	on: (event: string, handler: (event: ToolEvent, ctx: ProbeContext) => Promise<void>) => void;
};

export default function probe(pi: ProbeApi): void {
	pi.on("tool_call", async (event, ctx) => {
		if (!OUT) return;
		appendFileSync(OUT, JSON.stringify({
			tool: event.toolName,
			agentId: ctx.agentId,
			parentAgentId: ctx.parentAgentId,
		}) + "\n");
	});
}
