import { appendFileSync } from "node:fs";

const OUT = process.env.CTXPROBE_OUT || "/tmp/ctxprobe/out2.jsonl";

type ProbeContext = {
	getContextUsage?: () => unknown;
	sessionManager?: unknown;
};

type Handler = (event: unknown, ctx: ProbeContext) => Promise<void>;
type ProbeApi = { on: (event: string, handler: Handler) => void };

/** Every own + prototype member name, so accessors on the class show up too. */
function members(target: unknown): string[] {
	if (!target || (typeof target !== "object" && typeof target !== "function")) return [];
	const seen = new Set<string>();
	let cursor: object | null = target as object;
	while (cursor && cursor !== Object.prototype) {
		for (const name of Object.getOwnPropertyNames(cursor)) seen.add(name);
		cursor = Object.getPrototypeOf(cursor) as object | null;
	}
	return [...seen].sort();
}

/** Call a zero-arg member and stringify whatever comes back. */
function tryCall(target: unknown, name: string): string {
	if (!target || typeof target !== "object") return "no-target";
	const record = target as Record<string, unknown>;
	const value = record[name];
	try {
		const result = typeof value === "function" ? (value as () => unknown).call(target) : value;
		if (typeof result === "string") return result;
		if (result === undefined) return "undefined";
		if (result === null) return "null";
		return JSON.stringify(result)?.slice(0, 240) ?? typeof result;
	} catch (e) {
		return `THREW: ${String(e).slice(0, 80)}`;
	}
}

export default function probe(pi: ProbeApi): void {
	const session = Math.random().toString(36).slice(2, 6);
	let logged = false;

	pi.on("turn_end", async (_event, ctx) => {
		if (logged) return;
		logged = true;
		const sm = ctx?.sessionManager;
		const names = members(sm);
		const pathish = names.filter(n => /^(get|is)/.test(n) && /path|file|dir|id|name|session/i.test(n));
		const probed: Record<string, string> = {};
		for (const name of pathish) probed[name] = tryCall(sm, name);
		appendFileSync(
			OUT,
			JSON.stringify({
				session,
				usageDefined: ctx?.getContextUsage?.() !== undefined,
				sessionManagerType: typeof sm,
				memberCount: names.length,
				allMembers: names,
				probed,
			}) + "\n",
		);
	});
}
