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
    sampler: "#txt2img_sampling",
    scheduler: "#txt2img_scheduler",
    cfg: "#txt2img_cfg_scale",
    width: "#txt2img_width",
    height: "#txt2img_height",
    checkpoint: ".model_selection"
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

  function syncDisplayOnly(selector, value) {
    const input = inputInside(selector);
    if (!(input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement)) return false;
    const setter = nativeValueSetter(input);
    if (typeof setter !== "function") return false;
    // The checkpoint is already applied by Python. Update only the visible
    // textbox value: no input/change event, so Gradio cannot trigger another
    // checkpoint transition or tear down this bridge context.
    setter.call(input, String(value));
    return true;
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

  async function setChoice(selector, value, errorCode, bestEffort = false) {
    const root = document.querySelector(selector);
    if (!(root instanceof HTMLElement)) {
      if (bestEffort) return false;
      fail(errorCode);
    }

    const wanted = normalized(value);
    const radios = [...root.querySelectorAll("input[type='radio']")];
    for (const radio of radios) {
      const label = radio.closest("label") ?? root.querySelector(`label[for="${radio.id}"]`);
      const text = normalized(label?.textContent ?? radio.value);
      if (normalized(radio.value) === wanted || text === wanted) {
        if (radio.checked) return true;
        radio.click();
        await nextFrame();
        return true;
      }
    }

    const input = root.querySelector("input[role='combobox'], input:not([type='hidden'])");
    if (input instanceof HTMLInputElement) {
      input.focus();
      input.click();
      await nextFrame();
      // Gradio 4.40 DropdownOptions uses a short fly transition and commits
      // selection from the listbox's mousedown handler.
      await sleep(220);

      const listboxId = input.getAttribute("aria-controls");
      const getOptions = () => {
        const listbox = listboxId ? document.getElementById(listboxId) : null;
        return listbox instanceof HTMLElement
          ? [...listbox.querySelectorAll("[role='option']")]
          : [];
      };

      let options = getOptions();
      let exact = options.find(option =>
        normalized(option.getAttribute("aria-label") ?? option.textContent) === wanted);

      // Large Dropdowns render choices in batches. Ask Gradio to expose the
      // full list before deciding that a legitimate choice is missing.
      if (!(exact instanceof HTMLElement) && options.length > 0) {
        input.dispatchEvent(new KeyboardEvent("keydown", {
          key: "End",
          code: "End",
          bubbles: true,
          cancelable: true
        }));
        await nextFrame();
        await sleep(80);
        options = getOptions();
        exact = options.find(option =>
          normalized(option.getAttribute("aria-label") ?? option.textContent) === wanted);
      }

      if (exact instanceof HTMLElement) {
        // Do not trust the textbox display as current state: older bridge
        // versions could make it say Karras while Gradio still held Automatic.
        // aria-selected reflects Gradio's actual selected_index.
        if (exact.getAttribute("aria-selected") === "true") return true;

        exact.dispatchEvent(new MouseEvent("mousedown", {
          bubbles: true,
          cancelable: true,
          view: window,
          button: 0
        }));
        await nextFrame();
        await nextFrame();
        await sleep(40);

        // We never write the Dropdown textbox ourselves on this path. If it
        // now shows the requested label, that value came from Gradio's real
        // option-selection handler.
        if (normalized(input.value) === wanted) return true;
      }
    }

    if (bestEffort) return false;
    fail(errorCode);
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
    if (typeof settings.sampler === "string") await setChoice(selectors.sampler, settings.sampler, "sampler_missing");
    if (typeof settings.scheduler === "string") await setChoice(selectors.scheduler, settings.scheduler, "scheduler_missing");

    // Neo can finish a real checkpoint transition asynchronously after the
    // bridge has published the pending item. Pay the settle cost only when
    // Forge reports that the active checkpoint actually changed. A recipe
    // that already targets the current Model should remain responsive.
    if (payload.modelChanged === true) await sleep(3000);

    // The Python companion applies the checkpoint before publishing the
    // pending item. Synchronize only the visible dropdown text without
    // dispatching an input/change event. This keeps the UI honest without
    // triggering another Neo checkpoint refresh.
    if (typeof payload.appliedModel === "string")
      syncDisplayOnly(selectors.checkpoint, payload.appliedModel);

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
