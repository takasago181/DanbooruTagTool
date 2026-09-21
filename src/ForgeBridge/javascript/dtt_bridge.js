(() => {
  "use strict";

  if (window.__dttBridgeActive === true) return;
  window.__dttBridgeActive = true;

  const selectors = {
    positive: ["#txt2img_prompt textarea", "textarea#txt2img_prompt", 'textarea[aria-label="Prompt"]'],
    negative: ["#txt2img_neg_prompt textarea", "textarea#txt2img_neg_prompt", 'textarea[aria-label="Negative prompt"]'],
    generate: ["button#txt2img_generate", "#txt2img_generate button", "#txt2img_generate"],
    seed: "#txt2img_seed",
    steps: "#txt2img_steps",
    cfg: "#txt2img_cfg_scale",
    width: "#txt2img_width",
    height: "#txt2img_height"
  };
  const protocolVersion = 1;
  const consumerSessionKey = "dtt-bridge-consumer-id";
  let polling = false;

  function createConsumerId() {
    try {
      const existing = sessionStorage.getItem(consumerSessionKey);
      if (existing) return existing;
      const created = globalThis.crypto?.randomUUID?.() ??
        `tab-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      sessionStorage.setItem(consumerSessionKey, created);
      return created;
    } catch (_) {
      return `tab-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    }
  }

  const consumerId = createConsumerId();

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

  function inputInside(selector) {
    const root = document.querySelector(selector);
    if (root instanceof HTMLInputElement || root instanceof HTMLTextAreaElement) return root;
    return root?.querySelector("input:not([type='hidden']), textarea") ?? null;
  }

  function nativeValueSetter(element) {
    const prototype = element instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    return Object.getOwnPropertyDescriptor(prototype, "value")?.set;
  }

  function setValue(element, value) {
    const setter = nativeValueSetter(element);
    if (typeof setter !== "function") throw new Error("value_setter_missing");
    setter.call(element, String(value));
    if (typeof updateInput === "function") updateInput(element);
    else element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function nextFrame() {
    return new Promise(resolve => window.requestAnimationFrame(() => resolve()));
  }

  function sleep(milliseconds) {
    return new Promise(resolve => window.setTimeout(resolve, milliseconds));
  }

  function fail(code) {
    const error = new Error(code);
    error.dttCode = code;
    throw error;
  }

  function normalized(value) {
    return String(value ?? "").trim().toLowerCase();
  }

  function scalarEquivalent(current, requested) {
    const currentText = String(current ?? "").trim();
    const requestedText = String(requested ?? "").trim();
    const currentNumber = Number(currentText);
    const requestedNumber = Number(requestedText);
    if (currentText !== "" && requestedText !== "" &&
        Number.isFinite(currentNumber) && Number.isFinite(requestedNumber))
      return currentNumber === requestedNumber;
    return normalized(currentText) === normalized(requestedText);
  }

  function setScalar(selector, value, errorCode) {
    const input = inputInside(selector);
    if (!(input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement)) fail(errorCode);
    if (scalarEquivalent(input.value, value)) return false;
    setValue(input, value);
    return true;
  }

  async function applyRecipe(payload) {
    if (payload.serverError) fail(payload.serverError);
    const settings = payload.settings;
    if (!settings || typeof settings !== "object") return;

    if (settings.seed !== undefined) setScalar(selectors.seed, settings.seed, "seed_missing");
    if (settings.steps !== undefined) setScalar(selectors.steps, settings.steps, "steps_missing");
    if (settings.cfg !== undefined) setScalar(selectors.cfg, settings.cfg, "cfg_missing");
    if (settings.width !== undefined) setScalar(selectors.width, settings.width, "width_missing");
    if (settings.height !== undefined) setScalar(selectors.height, settings.height, "height_missing");

    await nextFrame();
    await nextFrame();
  }

  async function report(requestId, deliveryToken, success, error = "") {
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const response = await fetch("/dtt-bridge/result", {
          method: "POST",
          cache: "no-store",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ protocolVersion, requestId, deliveryToken, success, error })
        });
        if (!response.ok) return false;
        const envelope = await response.json();
        if (envelope.protocolVersion === protocolVersion &&
            envelope.accepted === true &&
            envelope.requestId === requestId)
          return true;
        return false;
      } catch (_) {
        if (attempt < 2) await sleep(150);
      }
    }
    // Keep the request pending. A later delivery lease can retry it safely.
    return false;
  }

  async function handle(payload) {
    const requestId = payload.requestId;
    const deliveryToken = payload.deliveryToken;
    const generate = payload.action === "send_and_generate";
    const applyOnly = payload.action === "apply_recipe";

    if (typeof deliveryToken !== "string" || !deliveryToken) return;

    const positive = findInput(selectors.positive);
    if (!positive || typeof payload.positive !== "string") {
      await report(requestId, deliveryToken, false, "positive_missing");
      return;
    }

    try {
      if (positive.value !== payload.positive)
        setValue(positive, payload.positive);

      if (payload.negativeMode === "replace") {
        const negative = findInput(selectors.negative);
        if (!negative || typeof payload.negative !== "string") {
          await report(requestId, deliveryToken, false, "negative_missing");
          return;
        }
        if (negative.value !== payload.negative)
          setValue(negative, payload.negative);
      }

      if (payload.settings) await applyRecipe(payload);

      if (generate) {
        const button = findClickable(selectors.generate);
        if (!button) {
          await report(requestId, deliveryToken, false, "generate_missing");
          return;
        }
        // A Generate click may refresh the Gradio tree immediately. Publish
        // the accepted action before that click so the browser context cannot
        // lose the ACK while Forge starts the job.
        if (!await report(requestId, deliveryToken, true, "")) return;
        await nextFrame();
        await nextFrame();
        button.click();
      } else {
        // Apply-only and legacy SendOnly both commit through /result so the
        // ACK-backed pending queue cannot retain a completed head forever.
        if (!await report(requestId, deliveryToken, true, "")) return;
      }
    } catch (error) {
      const code = typeof error?.dttCode === "string" ? error.dttCode : (generate ? "generate_failed" : "recipe_failed");
      await report(requestId, deliveryToken, false, code);
    }
  }

  async function poll() {
    if (polling) return;
    polling = true;
    try {
      const response = await fetch(`/dtt-bridge/pending?consumerId=${encodeURIComponent(consumerId)}`, { cache: "no-store" });
      if (!response.ok) return;
      const envelope = await response.json();
      const payload = envelope.pending;
      if (envelope.protocolVersion !== protocolVersion || !payload) return;
      if (typeof payload.requestId !== "string") return;
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
