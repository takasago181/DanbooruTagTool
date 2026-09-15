(() => {
  "use strict";

  // Forge currently exposes these stable txt2img component ids. The aria-label
  // selectors are a small compatibility fallback, kept in one place.
  const selectors = {
    positive: ["#txt2img_prompt textarea", "textarea#txt2img_prompt", 'textarea[aria-label="Prompt"]'],
    negative: ["#txt2img_neg_prompt textarea", "textarea#txt2img_neg_prompt", 'textarea[aria-label="Negative prompt"]']
  };
  const protocolVersion = 1;
  const bootedAt = Date.now();
  const sessionKey = "dtt-bridge-last-request-id";
  let polling = false;

  function find(selectorsToTry) {
    for (const selector of selectorsToTry) {
      const element = document.querySelector(selector);
      if (element instanceof HTMLTextAreaElement || element instanceof HTMLInputElement) return element;
    }
    return null;
  }

  function setValue(element, value) {
    const prototype = element instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(prototype, "value").set;
    setter.call(element, value);
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
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

      const positive = find(selectors.positive);
      if (!positive || typeof payload.positive !== "string") return;
      setValue(positive, payload.positive);

      // unchanged mode deliberately does not query or touch the Negative DOM.
      if (payload.negativeMode === "replace") {
        const negative = find(selectors.negative);
        if (negative && typeof payload.negative === "string") setValue(negative, payload.negative);
      }
      sessionStorage.setItem(sessionKey, payload.requestId);
    } catch (_) {
      // Forge may be starting up; the next short poll will retry health-free.
    } finally {
      polling = false;
    }
  }

  window.setInterval(poll, 700);
  window.setTimeout(poll, 250);
})();
