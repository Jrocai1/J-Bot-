import { createAgentNativeAgentKitTransport } from "@agent-native/core/client/agentkit-chat/transport";
import { useAgentThread } from "@agent-native/toolkit/app/agentkit/react/context";
import {
  CoreAgentKitRoot,
  CoreComposerRuntimeProvider,
} from "@agent-native/toolkit/app/chat/agentkit-chat";
import { AgentKitChat } from "@agent-native/toolkit/app/agentkit/react/components";
import { IconVolume, IconVolumeOff } from "@tabler/icons-react";
import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router";
import { toast } from "sonner";
import { TAB_ID } from "@/lib/tab-id";

const transport = createAgentNativeAgentKitTransport({
  browserTabId: TAB_ID,
  surface: "app",
  adapter: { textFormat: "markdown" },
});

export function meta() {
  return [{ title: "J-Bot Repair Session" }];
}

export default function RepairChatRoute() {
  const { threadId } = useParams();

  if (!threadId) return null;

  return <RepairChat threadId={threadId} />;
}

function RepairChat({ threadId }: { threadId: string }) {
  return (
    <div className="flex h-full min-h-[calc(100vh-68px)] flex-col">
      <CoreComposerRuntimeProvider>
        <CoreAgentKitRoot
          transport={transport}
          clientOptions={{ transportOwnership: "owned", retainActiveRunsOnThreadRelease: true }}
          threadId={threadId}
          onLoadError={() => toast.error("Could not load this repair session.")}
        >
          <SpeechControls threadId={threadId} />
          <InitialMessage threadId={threadId} />
          <AgentKitChat
            className="min-h-0 flex-1"
            title="J-Bot Repair Agent"
            emptyComposerPlacement="bottom"
            composerProps={{
              requireAgentEngine: true,
              placeholder: "Describe the issue or paste diagnostic evidence…",
            }}
          />
        </CoreAgentKitRoot>
      </CoreComposerRuntimeProvider>
    </div>
  );
}

function SpeechControls({ threadId }: { threadId: string }) {
  const thread = useAgentThread(threadId);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [gender, setGender] = useState<"female" | "male" | "auto">("auto");
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [speaking, setSpeaking] = useState(false);
  const lastSpokenId = useRef<string | null>(null);
  const latestAssistant = [...thread.messages].reverse().find((message) => message.role === "assistant");
  const latestText = latestAssistant?.parts
    .filter((part) => part.type === "text")
    .map((part) => part.text)
    .join("\n") ?? "";
  const thinking = thread.messages.at(-1)?.status === "streaming";
  const supported = typeof window !== "undefined" && "speechSynthesis" in window;

  useEffect(() => {
    if (!supported) return;
    const refreshVoices = () => setVoices(window.speechSynthesis.getVoices());
    refreshVoices();
    window.speechSynthesis.addEventListener("voiceschanged", refreshVoices);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", refreshVoices);
  }, [supported]);

  useEffect(() => {
    if (!voiceEnabled || !supported || !latestAssistant || latestAssistant.status !== "complete" || !latestText.trim() || lastSpokenId.current === latestAssistant.id) return;
    lastSpokenId.current = latestAssistant.id;
    const utterance = new SpeechSynthesisUtterance(latestText);
    const filtered = voices.filter((voice) => {
      if (gender === "auto") return true;
      return gender === "female"
        ? /female|samantha|zira|susan|karen|victoria|serena|moira|tessa|fiona|jenny|aria|ava/i.test(voice.name)
        : /male|daniel|david|mark|guy|fred|oliver|thomas|george|james|ryan|liam|brian|eric|joey/i.test(voice.name);
    });
    const voice = filtered.find((entry) => entry.lang.toLowerCase().startsWith("en")) ?? filtered[0];
    if (voice) utterance.voice = voice;
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
  }, [gender, latestAssistant, latestText, supported, voiceEnabled, voices]);

  function toggleVoice() {
    if (!supported) return;
    if (voiceEnabled) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      setVoiceEnabled(false);
      return;
    }
    lastSpokenId.current = latestAssistant?.id ?? null;
    setVoiceEnabled(true);
  }

  return (
    <div className="flex items-center gap-3 border-b border-border/70 px-5 py-3 md:px-8">
      <div className={`mini-robot ${thinking ? "robot-thinking" : ""}`} data-speaking={speaking}>
        <BotFace />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium">J-Bot Repair Agent</p>
        <p className="text-[10px] text-muted-foreground">{thinking ? "Thinking…" : speaking ? "Speaking" : "Conversation saved in the app database"}</p>
      </div>
      <label className="hidden items-center gap-2 text-[10px] text-muted-foreground sm:flex">
        Voice
        <select value={gender} onChange={(event) => setGender(event.target.value as typeof gender)} disabled={!supported} className="h-8 rounded-md border border-border bg-background px-2 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
          <option value="auto">Auto</option>
          <option value="female">Female</option>
          <option value="male">Male</option>
        </select>
      </label>
      <button type="button" onClick={toggleVoice} disabled={!supported} className="inline-flex h-8 items-center gap-1.5 rounded-md border border-border px-2.5 text-[10px] text-muted-foreground hover:bg-white/[0.04] disabled:opacity-45" aria-label={supported ? voiceEnabled ? "Turn voice off" : "Turn voice on" : "Speech synthesis unavailable"}>
        {voiceEnabled ? <IconVolume size={15} /> : <IconVolumeOff size={15} />}
        <span className="hidden sm:inline">{supported ? voiceEnabled ? "Voice on" : "Voice off" : "Voice unavailable"}</span>
      </button>
      {voiceEnabled && latestText.trim() && (
        <button type="button" onClick={() => { lastSpokenId.current = null; window.speechSynthesis.cancel(); setSpeaking(false); }} className="sr-only">Speak latest answer</button>
      )}
    </div>
  );
}

function InitialMessage({ threadId }: { threadId: string }) {
  const location = useLocation();
  const navigate = useNavigate();
  const control = useAgentKitControl(threadId);
  const sent = useRef(false);
  const initialMessage = (location.state as { initialMessage?: unknown } | null)?.initialMessage;

  useEffect(() => {
    if (sent.current || typeof initialMessage !== "string" || !initialMessage.trim()) return;
    sent.current = true;
    navigate({ pathname: location.pathname, search: location.search }, { replace: true, state: null });
    void control.sendMessage({ text: initialMessage }).catch((error: unknown) => {
      toast.error(error instanceof Error ? error.message : "Could not send the first message.");
    });
  }, [control, initialMessage, location.pathname, location.search, navigate]);

  return null;
}

function BotFace() {
  return (
    <svg viewBox="0 0 120 112" fill="none" aria-hidden="true" className="h-full w-full">
      <path d="M60 13v9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
      <circle cx="60" cy="10" r="4" className="robot-antenna" />
      <rect x="22" y="24" width="76" height="62" rx="22" className="robot-face" stroke="currentColor" strokeWidth="2.5" />
      <path d="M22 48H13a5 5 0 0 0-5 5v10a5 5 0 0 0 5 5h9m76-20h9a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5h-9" stroke="currentColor" strokeWidth="2.5" />
      <rect x="37" y="44" width="14" height="17" rx="7" className="robot-eye" />
      <rect x="69" y="44" width="14" height="17" rx="7" className="robot-eye" />
      <path d="M47 72c3.2 3 7.5 4.5 13 4.5s9.8-1.5 13-4.5" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" opacity=".8" className="robot-mouth" />
      <path d="M43 96h34" stroke="currentColor" strokeWidth="3" strokeLinecap="round" opacity=".55" />
    </svg>
  );
}
