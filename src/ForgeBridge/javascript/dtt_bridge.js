(() => {
  "use strict";

  // Forge currently exposes these stable txt2img component ids. Fallbacks are
  // kept in one place so compatibility changes stay isolated.
  const selectors = {
    positive: ["#txt2img_prompt textarea", "textarea#txt2img_prompt", 'textarea[aria-label="Prompt"]'],
    negative: ["#txt2img_neg_prompt textarea", "textarea#txt2img_neg_prompt", 'textarea[aria-label="Negative prompt"]'],
    generate: ["button#txt2img_generate", "#txt2img_generate button", "#txt2img_generate"]
  };
  const protocolVersion = 1;
  const bootedAt = Date.now();
  const sessionKey = "dtt-bridge-last-request-id";
  let polling = false;

  function findInput(selectorsToTry) {
    for (const selector of selectorsToTry) {
      const element = document.querySelector(selector);
      if (element instanceof HTMLTextAreaElement || element instanceof HTMLInputElement) return element;
    }
    return null;
  }

  function findClickable(selectorsToTry) {
    for (const selector of selectorsToTry) {
      const element = document.querySelector(selector);
      if (element instanceof HTMLElement) return element;
    }
    return null;
  }

  function setValue(element, value) {
    const prototype = element instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
    if (!descriptor || typeof descriptor.set !== "function") throw new Error("value_setter_missing");
    descriptor.set.call(element, value);
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function nextFrame() {
    return new Promise(resolve => window.requestAnimationFrame(() => resolve()));
  }

  async function report(requestId, success, error = "") {
    try {
      await fetch("/dtt-bridge/result", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ protocolVersion, requestId, success, error })
      });
    } catch (_) {
      // The desktop client will time out if the acknowledgement cannot be sent.
    }
  }

  async function handle(payload) {
    const requestId = payload.requestId;
    const generate = payload.action === "send_and_generate";

    const positive = findInput(selectors.positive);
    if (!positive || typeof payload.positive !== "string") {
      if (generate) await report(requestId, false, "positive_missing");
      return;
    }

    try {
      setValue(positive, payload.positive);

      // unchanged mode deliberately does not query or touch the Negative DOM.
      if (payload.negativeMode === "replace") {
        const negative = findInput(selectors.negative);
        if (!negative || typeof payload.negative !== "string") {
          if (generate) await report(requestId, false, "negative_missing");
          return;
        }
        setValue(negative, payload.negative);
      }

      if (generate) {
        const button = findClickable(selectors.generate);
        if (!button) {
          await report(requestId, false, "generate_missing");
          return;
        }

        // Let Gradio observe the Prompt input/change events before Generate.
        await nextFrame();
        await nextFrame();
        button.click();
        await report(requestId, true, "");
      }

      sessionStorage.setItem(sessionKey, requestId);
    } catch (_) {
      if (generate) await report(requestId, false, "generate_failed");
    }
  }

  async function poll() {
    if (polling) return;
    polling = true;
    try {
      const response = await fetch("/dtt-bridge/pending", { cache: "no-store" });
      if (!response.ok) return;
      const envelope = await response.json();
      const payload = envelope.pending;
      if (envelope.protocolVersion !== protocolVersion || !payload) return;
      if (typeof payload.requestId !== "string" || payload.createdAt < bootedAt) return;
      if (sessionStorage.getItem(sessionKey) === payload.requestId) return;
      await handle(payload);
    } catch (_) {
      // Forge may be starting up; the next short poll will retry health-free.
    } finally {
      polling = false;
    }
  }

  window.setInterval(poll, 700);
  window.setTimeout(poll, 250);
})();
