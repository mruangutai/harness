import { appendFileSync } from "node:fs";

const OUT = process.env.OMP_LINEAGE_PROBE_OUT;

type ProbeAgentIdentity = {
	kind: "main" | "sub";
	id: string;
	name: string;
	depth: number;
	parentId?: string;
};

type ProbeContext = {
	agent: ProbeAgentIdentity;
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
			agent: ctx.agent,
		}) + "\n");
	});
}
