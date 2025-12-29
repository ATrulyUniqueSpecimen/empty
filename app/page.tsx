"use client";

import { useEffect, useState } from "react";
import { Story } from "inkjs";

const SAVE_KEYS = ["ink_save_1", "ink_save_2", "ink_save_3"] as const;
const ACTIVE_SLOT_KEY = "ink_active_slot";

type ChoiceView = { index: number; text: string };

export default function Page() {
  const [story, setStory] = useState<Story | null>(null);
  const [lines, setLines] = useState<string[]>([]);
  const [choices, setChoices] = useState<ChoiceView[]>([]);
  const [activeSlot, setActiveSlot] = useState<number>(0); // 0..2

  function getSlotIndexFromStorage(): number {
    const raw = localStorage.getItem(ACTIVE_SLOT_KEY);
    const n = raw ? parseInt(raw, 10) : 0;
    if (Number.isFinite(n) && n >= 0 && n <= 2) return n;
    return 0;
  }

  function setActiveSlotPersisted(slot: number) {
    localStorage.setItem(ACTIVE_SLOT_KEY, String(slot));
    setActiveSlot(slot);
  }

  function saveToSlot(s: Story, slot: number) {
    localStorage.setItem(SAVE_KEYS[slot], s.state.toJson());
  }

  function loadFromSlot(s: Story, slot: number): boolean {
    const saved = localStorage.getItem(SAVE_KEYS[slot]);
    if (!saved) return false;
    try {
      s.state.LoadJson(saved);
      return true;
    } catch {
      // Corrupt save. Trash it.
      localStorage.removeItem(SAVE_KEYS[slot]);
      return false;
    }
  }

  function clearSlot(slot: number) {
    localStorage.removeItem(SAVE_KEYS[slot]);
  }

  function refreshUI(s: Story, resetTranscript: boolean) {
    // Rebuild transcript from the story's output since the last choice.
    // If resetTranscript is true, we throw away the old transcript.
    const newLines: string[] = [];
    while (s.canContinue) {
      const t = (s as any).Continue().trim();
      if (t) newLines.push(t);
    }

    if (resetTranscript) setLines(newLines);
    else if (newLines.length) setLines(prev => [...prev, ...newLines]);

    setChoices(s.currentChoices.map(c => ({ index: c.index, text: c.text })));
  }

  async function boot(slotToUse?: number) {
    const res = await fetch("/story.json");
    const json = await res.json();
    const s = new Story(json);

    const slot = slotToUse ?? getSlotIndexFromStorage();
    setActiveSlotPersisted(slot);

    const loaded = loadFromSlot(s, slot);

    setStory(s);

    // Important: If we loaded a save, rebuild transcript fresh from that state.
    // If we didn't, just start from the beginning.
    refreshUI(s, true);

    // If a save existed, we also immediately re-save, so any format upgrades
    // (or minor normalization) get persisted.
    if (loaded) saveToSlot(s, slot);
  }

  useEffect(() => {
    boot();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function choose(i: number) {
    if (!story) return;
    story.ChooseChoiceIndex(i);
    refreshUI(story, false);
    saveToSlot(story, activeSlot);
  }

  function switchSlot(slot: number) {
    if (slot === activeSlot) return;
    // Boot a fresh Story instance and load that slot into it.
    boot(slot);
  }

  function newGameInSlot(slot: number) {
    clearSlot(slot);
    // If you reset the active slot, restart immediately.
    if (slot === activeSlot) boot(slot);
  }

  function slotLabel(slot: number) {
    const hasSave = typeof window !== "undefined" && localStorage.getItem(SAVE_KEYS[slot]);
    return `Save ${slot + 1}${hasSave ? "" : " (empty)"}`;
  }

  return (
    <main style={{ maxWidth: 720, margin: "40px auto", padding: 16 }}>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 16 }}>
        {[0, 1, 2].map(slot => (
          <div key={slot} style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <button
              onClick={() => switchSlot(slot)}
              disabled={slot === activeSlot}
              style={{ minWidth: 140 }}
            >
              {slotLabel(slot)}
            </button>
            <button onClick={() => newGameInSlot(slot)}>New</button>
          </div>
        ))}
      </div>

      <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>
        {lines.map((t, idx) => (
          <p key={idx}>{t}</p>
        ))}
      </div>

      <div style={{ display: "grid", gap: 10, marginTop: 18 }}>
        {choices.map(c => (
          <button key={c.index} onClick={() => choose(c.index)}>
            {c.text}
          </button>
        ))}
      </div>
    </main>
  );
}