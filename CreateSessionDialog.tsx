import { useMemo, useState } from "react";
import {
  fetchAppModelDefault,
  saveAppModelDefault,
  type AppModelDefaultEngine,
} from "@agent-native/core/client/app-model-default";
import { buildSettingsRoute } from "@agent-native/core/client/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { IconCloud, IconDeviceDesktop, IconLoader2 } from "@tabler/icons-react";
import { Link } from "react-router";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

type Runtime = "local" | "online";

interface CreateSessionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreate: () => Promise<void>;
}

export function CreateSessionDialog({
  open,
  onOpenChange,
  onCreate,
}: CreateSessionDialogProps) {
  const queryClient = useQueryClient();
  const [runtime, setRuntime] = useState<Runtime>("local");
  const modelQuery = useQuery({
    queryKey: ["jbot", "app-model-default"],
    queryFn: fetchAppModelDefault,
    enabled: open,
  });
  const engines = modelQuery.data?.engines ?? [];
  const localEngine = engines.find((engine) => engine.name === "ai-sdk:ollama");
  const onlineEngines = engines.filter(
    (engine) => engine.name !== "ai-sdk:ollama" && engine.configured && engine.packageInstalled !== false,
  );
  const chosenEngine = runtime === "local"
    ? localEngine?.configured ? localEngine : undefined
    : onlineEngines.find((engine) => engine.name === modelQuery.data?.engine) ?? onlineEngines[0];
  const modelOptions = chosenEngine?.supportedModels ?? [];
  const model = chosenEngine?.defaultModel && modelOptions.includes(chosenEngine.defaultModel)
    ? chosenEngine.defaultModel
    : modelOptions[0] ?? chosenEngine?.defaultModel ?? "";
  const missingMessage = runtime === "local"
    ? "Connect Ollama and select an installed model in Model settings."
    : "Connect an online model provider in Model settings first.";
  const mutation = useMutation({
    mutationFn: async (engine: AppModelDefaultEngine) => {
      if (!modelQuery.data?.canUpdate) throw new Error("You do not have permission to change this app’s default model.");
      return saveAppModelDefault({ engine: engine.name, model });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["jbot", "app-model-default"] });
      await queryClient.invalidateQueries({ queryKey: ["action"] });
      await onCreate();
      onOpenChange(false);
    },
  });
  const selectedLabel = useMemo(() => chosenEngine?.label ?? "", [chosenEngine]);
  const canCreate = Boolean(chosenEngine && model && modelQuery.data?.canUpdate && !mutation.isPending);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="border-border bg-card sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>Start a repair session</DialogTitle>
          <DialogDescription>Choose the runtime for this and future sessions. History stays in the app database.</DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-2 gap-2 rounded-xl border border-border bg-background p-1.5">
          {([
            { value: "local", label: "Local AI", icon: IconDeviceDesktop, description: "Ollama on this machine" },
            { value: "online", label: "Online AI", icon: IconCloud, description: "Connected provider" },
          ] as const).map(({ value, label, icon: Icon, description }) => (
            <button
              key={value}
              type="button"
              onClick={() => { setRuntime(value); mutation.reset(); }}
              aria-pressed={runtime === value}
              className={`rounded-lg border p-3 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${runtime === value ? "border-cyan-300/50 bg-cyan-300/[0.08]" : "border-transparent hover:bg-white/[0.04]"}`}
            >
              <span className="flex items-center gap-2 text-sm font-medium"><Icon size={16} />{label}</span>
              <span className="mt-1 block text-[11px] text-muted-foreground">{description}</span>
            </button>
          ))}
        </div>
        {modelQuery.isLoading ? (
          <div className="flex items-center gap-2 py-3 text-xs text-muted-foreground"><IconLoader2 className="animate-spin" size={15} /> Checking configured model providers…</div>
        ) : modelQuery.isError ? (
          <p role="alert" className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-xs text-destructive">Could not read model configuration. Try again or open Model settings.</p>
        ) : chosenEngine ? (
          <div className="rounded-lg border border-border bg-background px-3 py-3">
            <p className="text-xs font-medium">{selectedLabel}</p>
            <p className="mt-1 text-[11px] text-muted-foreground">Model: {model || "No model selected"}</p>
            <p className="mt-2 text-[10px] leading-4 text-muted-foreground">This changes the app-wide default for new sessions. Existing session overrides are preserved.</p>
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-border p-3">
            <p className="text-xs text-muted-foreground">{missingMessage}</p>
            <Link to={buildSettingsRoute("model")} onClick={() => onOpenChange(false)} className="mt-2 inline-block text-xs font-medium text-cyan-200 hover:text-cyan-100">Open Model settings →</Link>
          </div>
        )}
        {mutation.isError && <p role="alert" className="text-xs text-destructive">{mutation.error.message}</p>}
        <DialogFooter className="gap-2 sm:gap-2">
          <button type="button" onClick={() => onOpenChange(false)} className="rounded-lg border border-border px-4 py-2 text-xs text-muted-foreground hover:bg-white/[0.04]">Cancel</button>
          <button type="button" disabled={!canCreate} onClick={() => chosenEngine && mutation.mutate(chosenEngine)} className="rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40">
            {mutation.isPending ? "Starting…" : "Create session"}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
