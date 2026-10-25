import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";
import { useChatThreads } from "@agent-native/toolkit/app/chat/agentkit-chat";
import { buildSettingsRoute } from "@agent-native/core/client/navigation";
import { CreateSessionDialog } from "@/components/chat/CreateSessionDialog";
import {
  IconActivity,
  IconArrowUp,
  IconBook2,
  IconCheck,
  IconChevronDown,
  IconCircleDot,
  IconDeviceMobile,
  IconFileText,
  IconHistory,
  IconLayoutDashboard,
  IconMenu2,
  IconPlus,
  IconSearch,
  IconSettings,
  IconShieldCheck,
  IconSparkles,
  IconUsb,
  IconX,
} from "@tabler/icons-react";
import { APP_TITLE } from "@/lib/app-config";

export function meta() {
  return [
    { title: `${APP_TITLE} — J-Bot Repair Agent` },
    { name: "description", content: "J-Bot AI repair workstation" },
  ];
}

const suggestions = [
  "Why is this phone not appearing over USB?",
  "Analyze a diagnostic report",
  "What does an error code mean?",
];

export default function HomeRoute() {
  const navigate = useNavigate();
  const { threads, createThread, switchThread } = useChatThreads(undefined, "jbot-chat-history", undefined, {
    autoCreate: false,
    restoreActiveThread: false,
  });
  const [draft, setDraft] = useState("");
  const [initialPrompt, setInitialPrompt] = useState("");
  const [sessionDialogOpen, setSessionDialogOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("Workspace");

  function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = draft.trim();
    if (!text) return;
    setInitialPrompt(text);
    setSessionDialogOpen(true);
  }

  async function createRepairSession() {
    const threadId = await createThread();
    if (!threadId) throw new Error("Could not create a repair session.");
    switchThread(threadId);
    navigate(`/chat/${encodeURIComponent(threadId)}`, {
      state: initialPrompt ? { initialMessage: initialPrompt } : undefined,
    });
    setDraft("");
    setInitialPrompt("");
  }

  function startSession() {
    setInitialPrompt("");
    setSessionDialogOpen(true);
  }

  return (
    <main className="jbot-app flex min-h-screen bg-background text-foreground">
      <aside className="jbot-sidebar hidden w-[236px] shrink-0 flex-col border-r border-border/70 px-4 py-5 lg:flex">
        <div className="mb-9 flex items-center gap-3 px-2">
          <div className="brand-mark"><BotMark /></div>
          <div>
            <p className="text-[15px] font-semibold tracking-tight">J-ROC <span className="text-cyan-300">AI</span></p>
            <p className="mt-0.5 text-[10px] uppercase tracking-[0.18em] text-muted-foreground">Repair workstation</p>
          </div>
        </div>
        <button onClick={startSession} className="new-session mb-7 flex h-10 items-center justify-center gap-2 rounded-lg px-3 text-sm font-medium transition hover:brightness-110">
          <IconPlus size={17} /> New repair session
        </button>
        <p className="section-label px-3">WORKSPACE</p>
        <nav className="mt-2 space-y-1" aria-label="Main navigation">
          {[
            { label: "Workspace", icon: IconLayoutDashboard },
            { label: "Knowledge base", icon: IconBook2 },
            { label: "Session history", icon: IconHistory },
          ].map(({ label, icon: Icon }) => (
            <button key={label} onClick={() => setActiveSection(label)} className={`nav-link flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-[13px] transition ${activeSection === label ? "nav-link-active" : "text-muted-foreground hover:bg-white/[0.04] hover:text-foreground"}`}>
              <Icon size={17} stroke={1.7} /> {label}
              {label === "Workspace" && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-cyan-300" />}
            </button>
          ))}
        </nav>
        <div className="mt-8">
          <p className="section-label px-3">RECENT SESSIONS</p>
          <div className="mt-3 space-y-1">
            {threads.length ? threads.slice(0, 6).map((thread) => (
              <button key={thread.id} onClick={() => { switchThread(thread.id); navigate(`/chat/${encodeURIComponent(thread.id)}`); }} className="w-full truncate rounded-lg px-3 py-2 text-left text-xs text-muted-foreground hover:bg-white/[0.04] hover:text-foreground">
                {thread.title || thread.preview || "Untitled repair session"}
              </button>
            )) : <div className="rounded-lg border border-dashed border-border/80 px-3 py-4 text-xs leading-5 text-muted-foreground"><IconHistory size={17} className="mb-2 opacity-70" /><p>No saved sessions yet.</p><p className="text-[11px]">Your conversations will appear here.</p></div>}
          </div>
        </div>
        <div className="mt-auto border-t border-border/70 pt-4">
          <Link to={buildSettingsRoute("model")} className="nav-link flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-[13px] text-muted-foreground hover:bg-white/[0.04] hover:text-foreground">
            <IconSettings size={17} stroke={1.7} /> Models & providers
          </Link>
          <div className="mt-4 flex items-center gap-2 rounded-lg border border-border/70 bg-white/[0.025] px-3 py-2.5">
            <span className="status-dot bg-amber-300" />
            <span className="text-[11px] text-muted-foreground">Agent chat · model configured separately</span>
          </div>
        </div>
      </aside>

      <section className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-[68px] shrink-0 items-center justify-between border-b border-border/70 px-5 md:px-8">
          <div className="flex items-center gap-3">
            <button className="rounded-md p-2 text-muted-foreground hover:bg-white/[0.05] lg:hidden" aria-label="Open navigation"><IconMenu2 size={19} /></button>
            <div className="flex items-center gap-2 text-sm"><span className="text-muted-foreground">{activeSection}</span><IconChevronDown size={14} className="text-muted-foreground/60" /></div>
          </div>
          <div className="flex items-center gap-3">
            <Link to={buildSettingsRoute("model")} className="hidden items-center gap-2 rounded-full border border-border/80 px-3 py-1.5 transition hover:border-cyan-300/30 hover:bg-cyan-300/[0.04] sm:flex"><span className="status-dot bg-cyan-300" /><span className="text-[11px] text-muted-foreground">Models & providers</span></Link>
            <button onClick={startSession} className="rounded-md border border-border/80 p-2 text-muted-foreground transition hover:bg-white/[0.05] hover:text-foreground" aria-label="Start new session"><IconPlus size={17} /></button>
          </div>
        </header>

        <div className="grid min-h-0 flex-1 grid-cols-1 2xl:grid-cols-[minmax(0,1fr)_300px]">
          <div className="flex min-h-[calc(100vh-68px)] min-w-0 flex-col">
            <div className="flex flex-1 flex-col items-center px-5 pb-5 pt-7 md:px-8">
              <div className="w-full max-w-[820px]">
                <div className="mb-6 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-[11px] text-muted-foreground"><span className="h-1.5 w-1.5 rounded-full bg-cyan-300" /> NO ACTIVE SESSION</div>
                  <button className="flex items-center gap-1.5 rounded-md px-2 py-1 text-[11px] text-muted-foreground hover:bg-white/[0.04]"><IconShieldCheck size={14} /> Safety policy <IconChevronDown size={12} /></button>
                </div>

                <div className="welcome-stage flex min-h-[390px] flex-col items-center justify-center pb-3 text-center">
                    <div className="robot-aura"><div className="robot-shell"><RobotAvatar /></div></div>
                    <p className="mt-6 text-[11px] font-medium uppercase tracking-[0.2em] text-cyan-200/80">J-Bot Repair Agent</p>
                    <h1 className="mt-2 text-3xl font-semibold tracking-[-0.04em] sm:text-[38px]">Let’s solve it safely.</h1>
                    <p className="mt-3 max-w-[460px] text-sm leading-6 text-muted-foreground">Describe the issue or share diagnostic evidence. J-Bot will use verified sources and explain what it can—and can’t—confirm.</p>
                    <div className="mt-7 grid w-full max-w-[650px] gap-2 sm:grid-cols-3">
                      {suggestions.map((suggestion, index) => (
                        <button key={suggestion} onClick={() => setDraft(suggestion)} className="suggestion-card group rounded-xl p-3.5 text-left text-xs leading-5 text-foreground/80 transition hover:-translate-y-0.5 hover:border-cyan-300/40 hover:bg-cyan-300/[0.06]">
                          <span className="mb-2 flex h-7 w-7 items-center justify-center rounded-md bg-cyan-300/[0.09] text-cyan-200">{index === 0 ? <IconUsb size={16} /> : index === 1 ? <IconFileText size={16} /> : <IconSearch size={16} />}</span>
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
              </div>
              <div className="mt-auto w-full max-w-[820px] pt-6">
                <form onSubmit={sendMessage} className="composer rounded-2xl p-2.5 transition focus-within:border-cyan-300/40">
                  <textarea value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} rows={2} placeholder="Describe the device issue or paste diagnostic evidence…" className="w-full resize-none bg-transparent px-3 py-2.5 text-sm leading-6 outline-none placeholder:text-muted-foreground/65" aria-label="Describe the device issue or paste diagnostic evidence" />
                  <div className="flex items-center justify-between px-1 pb-0.5">
                    <div className="flex items-center gap-2 text-[10px] text-muted-foreground"><IconShieldCheck size={14} className="text-cyan-200/80" /> No repair actions run without approval</div>
                    <button type="submit" disabled={!draft.trim()} className="send-button flex h-9 w-9 items-center justify-center rounded-lg text-slate-950 transition disabled:cursor-not-allowed disabled:opacity-35" aria-label="Send message"><IconArrowUp size={19} /></button>
                  </div>
                </form>
                <p className="mt-2 text-center text-[10px] text-muted-foreground/65">Advice is not a substitute for verified device-specific service documentation.</p>
              </div>
            </div>
          </div>

          <aside className="right-rail hidden border-l border-border/70 px-4 py-5 2xl:block">
            <div className="mb-4 flex items-center justify-between"><h2 className="text-xs font-semibold tracking-wide">Session context</h2><button aria-label="Close session context" className="rounded p-1 text-muted-foreground hover:bg-white/[0.05]"><IconX size={15} /></button></div>
            <section className="context-panel rounded-xl p-4">
              <div className="mb-3 flex items-center justify-between"><span className="text-xs font-medium">Connected device</span><IconDeviceMobile size={16} className="text-muted-foreground" /></div>
              <div className="rounded-lg border border-dashed border-border/80 px-3 py-4 text-center">
                <div className="mx-auto mb-2 flex h-9 w-9 items-center justify-center rounded-full bg-white/[0.035] text-muted-foreground"><IconUsb size={18} /></div>
                <p className="text-xs font-medium">No device detected</p><p className="mt-1 text-[10px] leading-4 text-muted-foreground">Connect a device or provide diagnostic evidence to begin.</p>
              </div>
              <button className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg border border-border/80 py-2 text-[11px] text-muted-foreground hover:bg-white/[0.04]"><IconActivity size={14} /> Device discovery unavailable</button>
            </section>
            <section className="context-panel mt-3 rounded-xl p-4">
              <div className="mb-3 flex items-center justify-between"><span className="text-xs font-medium">Agent activity</span><span className="text-[10px] text-muted-foreground">LIVE</span></div>
              <div className="space-y-3">
                {[{ label: "Evidence collection", state: "Waiting for request" }, { label: "Knowledge retrieval", state: "Not started" }, { label: "Diagnosis & plan", state: "Not started" }, { label: "Verification", state: "Not started" }].map((item, index) => (
                  <div key={item.label} className="flex gap-2.5"><span className={`mt-1 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border ${index === 0 ? "border-amber-300/50 text-amber-200" : "border-border text-muted-foreground/50"}`}>{index === 0 ? <IconCircleDot size={10} /> : <IconCheck size={9} />}</span><div><p className="text-[11px] leading-4">{item.label}</p><p className="text-[10px] text-muted-foreground">{item.state}</p></div></div>
                ))}
              </div>
            </section>
            <section className="context-panel mt-3 rounded-xl p-4">
              <div className="mb-2 flex items-center gap-2"><IconBook2 size={15} className="text-cyan-200" /><span className="text-xs font-medium">Knowledge sources</span></div>
              <p className="text-[10px] leading-4 text-muted-foreground">No verified knowledge corpus is connected. Recommendations will not include fabricated citations.</p>
              <button onClick={() => setActiveSection("Knowledge base")} className="mt-3 text-[10px] font-medium text-cyan-200 hover:text-cyan-100">Browse knowledge base <span aria-hidden="true">→</span></button>
            </section>
            <div className="mt-4 flex items-center gap-2 px-1 text-[10px] text-muted-foreground"><IconSparkles size={14} className="text-cyan-200/70" /> Local-first · approval-gated</div>
          </aside>
        </div>
      </section>
      <CreateSessionDialog open={sessionDialogOpen} onOpenChange={setSessionDialogOpen} onCreate={createRepairSession} />
    </main>
  );
}

function RobotAvatar() {
  return (
    <svg viewBox="0 0 120 112" fill="none" role="img" aria-label="J-Bot robot avatar" className="h-full w-full">
      <path d="M60 13v9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
      <circle cx="60" cy="10" r="4" className="robot-antenna" />
      <rect x="22" y="24" width="76" height="62" rx="22" className="robot-face" stroke="currentColor" strokeWidth="2.5" />
      <path d="M22 48H13a5 5 0 0 0-5 5v10a5 5 0 0 0 5 5h9m76-20h9a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5h-9" stroke="currentColor" strokeWidth="2.5" />
      <rect x="37" y="44" width="14" height="17" rx="7" className="robot-eye" />
      <rect x="69" y="44" width="14" height="17" rx="7" className="robot-eye" />
      <path d="M47 72c3.2 3 7.5 4.5 13 4.5s9.8-1.5 13-4.5" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" opacity=".8" />
      <path d="M43 96h34" stroke="currentColor" strokeWidth="3" strokeLinecap="round" opacity=".55" />
    </svg>
  );
}

function BotMark() {
  return <div className="h-7 w-7"><RobotAvatar /></div>;
}
